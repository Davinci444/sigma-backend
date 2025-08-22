# Archivo: flota/management/commands/importar_tanqueos.py

from django.core.management.base import BaseCommand
from flota.models import Vehiculo, Tanqueo
import pandas as pd

class Command(BaseCommand):
    help = 'Importa registros de tanqueo desde el archivo GESTION DE COMBUSTIBLE.xlsx'

    def handle(self, *args, **kwargs):
        # La ruta ahora apunta al archivo .xlsx
        file_path = 'GESTION DE COMBUSTIBLE.xlsx'
        # El nombre de la hoja de la que leeremos los datos
        sheet_name = 'TANQUEOS'
        
        self.stdout.write(self.style.SUCCESS(f'Iniciando importación desde "{file_path}" (Hoja: "{sheet_name}")...'))

        placas_propias = set(Vehiculo.objects.values_list('placa', flat=True))
        registros_creados = 0
        registros_omitidos = 0

        try:
            # Usamos pd.read_excel() para leer el archivo y la hoja específica
            df = pd.read_excel(file_path, sheet_name=sheet_name)

            for index, row in df.iterrows():
                placa = str(row.get('PLACA')).strip() if pd.notna(row.get('PLACA')) else None

                if placa and placa in placas_propias:
                    try:
                        vehiculo = Vehiculo.objects.get(placa=placa)
                        
                        fecha = row.get('FECHA')
                        kilometraje = pd.to_numeric(row.get('KILOMETRAJE'), errors='coerce')
                        galones = pd.to_numeric(row.get('GALONES'), errors='coerce')

                        if pd.isna(fecha) or pd.isna(kilometraje) or pd.isna(galones):
                            self.stdout.write(self.style.WARNING(f'Omitiendo fila {index+2}: Datos esenciales faltantes.'))
                            registros_omitidos += 1
                            continue
                        
                        # Usamos get_or_create para evitar duplicados si se corre el script varias veces
                        obj, created = Tanqueo.objects.get_or_create(
                            vehiculo=vehiculo,
                            fecha=fecha,
                            kilometraje=int(kilometraje),
                            defaults={'galones': galones}
                        )

                        if created:
                            registros_creados += 1
                        else:
                            registros_omitidos += 1 # Ya existía, lo contamos como omitido

                    except Vehiculo.DoesNotExist:
                        registros_omitidos += 1
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'Error procesando la fila {index+2}: {e}'))
                        registros_omitidos += 1
                else:
                    registros_omitidos += 1

            self.stdout.write(self.style.SUCCESS(f'--- Importación Finalizada ---'))
            self.stdout.write(self.style.SUCCESS(f'Registros nuevos creados: {registros_creados}'))
            self.stdout.write(self.style.WARNING(f'Registros omitidos (placas de terceros, duplicados o datos inválidos): {registros_omitidos}'))

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'Error: No se encontró el archivo en la ruta: {file_path}. Asegúrate de que esté al mismo nivel que manage.py.'))
        except ValueError as ve:
             self.stdout.write(self.style.ERROR(f'Error: La hoja "{sheet_name}" no se encontró en el archivo Excel. Error: {ve}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Un error inesperado ocurrió: {e}'))