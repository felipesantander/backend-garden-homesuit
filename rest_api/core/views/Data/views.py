import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from core.models import Channel, Data, Machine
from core.validators import DataValidator


@csrf_exempt
def ingest_data(request):
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

        # Create Data object
        data_obj = Data.objects.create(
            dataId=payload["dataId"],
            frequency=payload["frequency"],
            value=payload["value"],
            type=payload["type"],
            serial_machine=payload["serial_machine"],
            machineId=machine,
            channelId=channel,
        )

        return JsonResponse({"message": "Data ingested successfully", "id": data_obj.idData}, status=201)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
