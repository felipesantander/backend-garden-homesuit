import json
from datetime import datetime

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from core.models import Channel, Data, Machine
from core.serializers import DataSerializer
from core.serializers.Data.query import DataQuerySerializer
from core.validators.data.insert import DataValidator


class DataViewSet(viewsets.ModelViewSet):
    queryset = Data.objects.all()
    serializer_class = DataSerializer

    @action(detail=False, methods=["get"])
    def latest(self, request):
        serial = request.query_params.get("serial")
        if not serial:
            return Response({"error": "Serial parameter is required"}, status=400)

        # Get all unique types for this serial
        data_types = Data.objects.filter(serial_machine=serial).values_list("type", flat=True).distinct()

        latest_data = {}
        for d_type in data_types:
            # Get the latest bucket for this type
            latest_bucket = (
                Data.objects.filter(serial_machine=serial, type=d_type).order_by("-base_date").first()
            )
            if latest_bucket and latest_bucket.readings:
                # Return the last reading in the bucket
                latest_data[d_type] = latest_bucket.readings[-1]

        return Response(latest_data)

    @action(detail=False, methods=["get"])
    def query(self, request):
        serializer = DataQuerySerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response(serializer.errors, status=400)

        validated_data = serializer.validated_data
        machine_id = validated_data["machineId"]
        channel_list = validated_data.get("channels", [])
        start_dt = validated_data.get("start")
        end_dt = validated_data.get("end")
        f_filter = validated_data.get("f")

        queryset = Data.objects.filter(machineId=machine_id).select_related('channelId')

        if channel_list:
            queryset = queryset.filter(channelId__in=channel_list)

        if f_filter:
            queryset = queryset.filter(frequency=f_filter)

        if start_dt:
            start_base = start_dt.replace(minute=0, second=0, microsecond=0)
            queryset = queryset.filter(base_date__gte=start_base)

        if end_dt:
            queryset = queryset.filter(base_date__lte=end_dt)

        results = []
        for bucket in queryset.order_by("base_date"):
            for reading in bucket.readings:
                try:
                    r_time = datetime.fromisoformat(reading["t"].replace('Z', '+00:00'))
                except ValueError:
                    continue
                
                if start_dt and r_time < start_dt:
                    continue
                if end_dt and r_time > end_dt:
                    continue
                
                if f_filter and reading.get("f") != f_filter:
                    continue
                
                results.append({
                    "machineId": str(bucket.machineId_id),
                    "channelId": str(bucket.channelId_id),
                    "type": bucket.channelId.name,
                    "value": reading["v"],
                    "timestamp": reading["t"],
                    "frequency": reading["f"]
                })

        return Response(results)


@csrf_exempt
def ingest_data(request):
    print(f"DEBUG: ingest_data called with method={request.method} path={request.path}")
    if request.method != "POST":
        return JsonResponse({"error": "Only POST method is allowed"}, status=405)

    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    validator = DataValidator()
    is_valid, errors = validator.validate(payload)

    if not is_valid:
        return JsonResponse({"error": "Validation failed", "details": errors}, status=400)

    from core.models.data_manager import DataBucketManager
    db = DataBucketManager.get_db()
    
    try:
        # Fetch related objects
        try:
            machine = Machine.objects.get(machineId=payload["machineId"])
        except Machine.DoesNotExist:
            return JsonResponse({"error": f"Machine with id {payload['machineId']} does not exist"}, status=404)

        try:
            channel = Channel.objects.get(idChannel=payload["channelId"])
        except Channel.DoesNotExist:
            return JsonResponse({"error": f"Channel with id {payload['channelId']} does not exist"}, status=404)

        # Add reading to bucket
        DataBucketManager.add_reading(
            machine=machine,
            channel=channel,
            data_type=payload["type"],
            value=payload["value"],
            timestamp=payload.get("date_of_capture"),
            frequency=payload["frequency"],
            serial_machine=payload["serial_machine"]
        )

        return JsonResponse({
            "message": "Data ingested into bucket successfully",
            "db": DataBucketManager.get_db().name
        }, status=201)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
