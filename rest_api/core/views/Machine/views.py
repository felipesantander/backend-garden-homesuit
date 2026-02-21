from django.db import transaction, IntegrityError
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from core.models import Machine, Channel, ConfigurationChannel
from core.serializers import MachineSerializer
from core.serializers.Machine.register import MachineRegistrationSerializer


class MachineViewSet(viewsets.ModelViewSet):
    queryset = Machine.objects.all()
    serializer_class = MachineSerializer

    @action(detail=False, methods=["post"])
    def register(self, request):
        serializer_reg = MachineRegistrationSerializer(data=request.data)
        if not serializer_reg.is_valid():
            return Response(serializer_reg.errors, status=status.HTTP_400_BAD_REQUEST)

        validated_data = serializer_reg.validated_data
        serial = validated_data["serial"]
        name = validated_data["Name"]
        garden_id = validated_data.get("garden")
        supported_frequencies = validated_data.get("supported_frequencies", [])
        dashboard_frequency = validated_data.get("dashboardFrequency", "1_minutes")
        configurations = validated_data.get("configurations", [])

        try:
            # Create Machine
            machine = Machine.objects.create(
                serial=serial,
                Name=name,
                garden_id=garden_id,
                supported_frequencies=supported_frequencies,
                dashboardFrequency=dashboard_frequency
            )

            try:
                # Create Channel Configurations
                created_configs = []
                for config in configurations:
                    c_type = config["type"]
                    channel_id = config["channel"]

                    channel = Channel.objects.get(idChannel=channel_id)

                    conf_obj = ConfigurationChannel.objects.create(
                        machine=machine,
                        type=c_type,
                        channel=channel,
                        serial=serial
                    )
                    created_configs.append({
                        "id": str(conf_obj.idConfigurationChannel),
                        "type": c_type,
                        "channel": str(channel.idChannel),
                        "channel_name": channel.name
                    })

                serializer = self.get_serializer(machine)
                data = serializer.data
                data["configurations"] = created_configs
                return Response(data, status=status.HTTP_201_CREATED)

            except Exception as e:
                # Manual rollback: Delete the machine (this will delete configs too due to CASCADE)
                machine.delete()
                raise e

        except (ValueError, IntegrityError) as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": f"An unexpected error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
