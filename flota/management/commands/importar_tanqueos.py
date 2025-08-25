# Archivo: flota/management/commands/importar_tanqueos.py
from django.core.management.base import BaseCommand
from flota.models import Vehiculo, Tanqueo
import pandas as pd
from django.db.models import Max
from django.utils.timezone import make_aware
import pytz

class Command(BaseCommand):
    help = 'Importa NUEVOS registros de tanqueo desde el archivo GESTION DE COMBUSTIBLE.xlsx'

    def handle(self, *args, **kwargs):
        file_path = 'GESTION DE COMBUSTIBLE.xlsx'
        sheet_name = 'TANQUEOS'
        
        self.stdout.write(self.style.SUCCESS(f'Iniciando sincronización desde "{file_path}"...'))

        placas_propias = set(Vehiculo.objects.values_list('placa', flat=True))

        ultimos_tanqueos = {
            item['vehiculo__placa']: item['ultima_fecha']
            for item in Tanqueo.objects.values('vehiculo__placa').annotate(ultima_fecha=Max('fecha'))
        }

        registros_nuevos = 0
        registros_antiguos = 0
        registros_omitidos = 0
        
        try:
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            df = df.dropna(subset=['FECHA', 'PLACA', 'KILOMETRAJE', 'GALONES'])

            for index, row in df.iterrows():
                placa = str(row['PLACA']).strip() if pd.notna(row['PLACA']) else None
                
                if placa in placas_propias:
                    try:
                        fecha_excel = pd.to_datetime(row['FECHA'])
                        fecha_excel_aware = make_aware(fecha_excel, timezone=pytz.timezone('America/Bogota'))
                        ultima_fecha_db = ultimos_tanqueos.get(placa)

                        if not ultima_fecha_db or fecha_excel_aware > ultima_fecha_db:
                            vehiculo = Vehiculo.objects.get(placa=placa)
                            Tanqueo.objects.create(
                                vehiculo=vehiculo,
                                fecha=fecha_excel_aware,
                                kilometraje=int(row['KILOMETRAJE']),
                                galones=float(row['GALONES']),
                                conductor=row.get('CONDUCTOR')
                            )
                            registros_nuevos += 1
                        else:
                            registros_antiguos += 1
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'Error en fila {index+2}: {e}'))
                        registros_omitidos += 1
                else:
                    registros_omitidos += 1
            
            self.stdout.write(self.style.SUCCESS('--- Sincronización Finalizada ---'))
            self.stdout.write(self.style.SUCCESS(f'Registros nuevos añadidos: {registros_nuevos}'))
            self.stdout.write(self.style.NOTICE(f'Registros antiguos ignorados: {registros_antiguos}'))
            self.stdout.write(self.style.WARNING(f'Registros omitidos (placas de terceros, etc.): {registros_omitidos}'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error Crítico: {e}'))