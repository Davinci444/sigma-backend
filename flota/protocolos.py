# Archivo: flota/protocolos.py

PROTOCOLOS_PREVENTIVOS = {
    'GASOLINA': [
        {
            'nombre': 'Servicio Preventivo 10.000km',
            'kilometraje': 10000,
            'tareas': [
                "Cambio de aceite y filtro de aceite.",
                "Revisión de niveles y fugas.",
                "Revisión de presión de neumáticos y rotación.",
                "Inspección de frenos.",
            ]
        },
        {
            'nombre': 'Servicio Preventivo 20.000km',
            'kilometraje': 20000,
            'tareas': [
                "Cambio de filtro de aire.",
                "Cambio de filtro de aire de cabina (antipolen).",
                "Inspección de suspensión y dirección.",
            ]
        },
        {
            'nombre': 'Servicio Preventivo 40.000km',
            'kilometraje': 40000,
            'tareas': [
                "Cambio de líquido de frenos.",
                "Cambio de bujías.",
            ]
        },
        {
            'nombre': 'Servicio Preventivo 60.000km',
            'kilometraje': 60000,
            'tareas': [
                "Cambio de correa de accesorios.",
            ]
        },
    ],
    'DIESEL': [
        {
            'nombre': 'Servicio Preventivo 10.000km',
            'kilometraje': 10000,
            'tareas': [
                "Cambio de aceite y filtro de aceite.",
                "Cambio de filtro de combustible.",
                "Revisión de niveles y fugas.",
                "Revisión de presión de neumáticos y rotación.",
                "Inspección de frenos.",
            ]
        },
        {
            'nombre': 'Servicio Preventivo 20.000km',
            'kilometraje': 20000,
            'tareas': [
                "Cambio de filtro de aire.",
                "Cambio de filtro de aire de cabina.",
            ]
        },
        {
            'nombre': 'Servicio Preventivo 60.000km',
            'kilometraje': 60000,
            'tareas': [
                "Cambio de correa de accesorios.",
                "Revisión del sistema de inyección.",
            ]
        },
    ]
}

def get_tareas_para_kilometraje(tipo_motor, kilometraje_vehiculo, km_activacion_plan):
    if km_activacion_plan is None or km_activacion_plan == 0:
        return [], "Plan no activado"

    km_recorridos_en_plan = kilometraje_vehiculo - km_activacion_plan
    protocolo = PROTOCOLOS_PREVENTIVOS.get(tipo_motor, [])
    
    if km_recorridos_en_plan < 0: km_recorridos_en_plan = 0
    ciclo_actual = round(km_recorridos_en_plan / 10000) * 10000

    tareas_acumuladas = []
    plan_toca = "Servicio General"

    planes_aplicables = []
    for plan in protocolo:
        intervalo = plan['kilometraje']
        if ciclo_actual > 0 and (ciclo_actual % intervalo) == 0:
            planes_aplicables.append(plan)
    
    if planes_aplicables:
        plan_elegido = max(planes_aplicables, key=lambda x: x['kilometraje'])
        plan_toca = plan_elegido['nombre']
        for p in planes_aplicables:
            tareas_acumuladas.extend(p['tareas'])

    return list(set(tareas_acumuladas)), plan_toca