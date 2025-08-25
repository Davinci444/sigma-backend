# Archivo: flota/management/commands/importar_tanqueos.py

from django.core.management.base import BaseCommand
from flota.models import Vehiculo, Tanqueo
import pandas as pd
from django.db.models import Max
from django.utils.timezone import make_aware
import pytz
from datetime import datetime, time

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
            df = df.dropna(subset=['PLACA', 'KILOMETRAJE', 'GALONES'])

            last_valid_date = None # Variable para recordar la última fecha completa

            for index, row in df.iterrows():
                placa = str(row['PLACA']).strip() if pd.notna(row['PLACA']) else None
                
                if placa in placas_propias:
                    try:
                        # --- NUEVA LÓGICA PARA CORREGIR FECHAS ---
                        fecha_cell = row.get('FECHA')

                        if isinstance(fecha_cell, datetime):
                            fecha_actual = fecha_cell
                            last_valid_date = fecha_actual.date() # Guardamos la parte de la fecha
                        elif isinstance(fecha_cell, time) and last_valid_date:
                            # Si solo tenemos una hora, la combinamos con la última fecha válida
                            fecha_actual = datetime.combine(last_valid_date, fecha_cell)
                        else:
                            # Si no podemos determinar la fecha, omitimos la fila
                            registros_omitidos += 1
                            continue
                        
                        fecha_actual_aware = make_aware(fecha_actual, timezone=pytz.timezone('America/Bogota'))
                        ultima_fecha_db = ultimos_tanqueos.get(placa)

                        if not ultima_fecha_db or fecha_actual_aware > ultima_fecha_db:
                            vehiculo = Vehiculo.objects.get(placa=placa)
                            Tanqueo.objects.create(
                                vehiculo=vehiculo,
                                fecha=fecha_actual_aware,
                                kilometraje=int(row['KILOMETRAJE']),
                                galones=float(row['GALONES']),
                                conductor=row.get('CONDUCTOR')
                            )
                            # Actualizamos el diccionario en memoria para la siguiente iteración
                            ultimos_tanqueos[placa] = fecha_actual_aware
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