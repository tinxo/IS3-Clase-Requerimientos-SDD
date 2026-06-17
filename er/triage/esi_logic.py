def sugerir_nivel_esi(signos_vitales, dolor_eva, glasgow, via_aerea, motivo):
    """
    Sugiere nivel ESI basado en signos vitales y evaluaciones.
    
    Returns:
        int: Nivel ESI sugerido (1-5)
        str: Justificación de la sugerencia
    """
    
    # ESI 1: Condiciones críticas
    if via_aerea == 'obstruida':
        return 1, "Vía aérea obstruida - Requiere intervención inmediata"
    
    if glasgow and glasgow < 8:
        return 1, "Glasgow < 8 - Estado crítico de conciencia"
    
    if signos_vitales.get('saturacion_o2') is not None and signos_vitales['saturacion_o2'] < 85:
        return 1, "Saturación O2 crítica"
    
    # ESI 2: Emergencia
    if glasgow and glasgow < 14:
        return 2, "Glasgow < 14 - Alteración del nivel de conciencia"
    
    if signos_vitales.get('saturacion_o2') is not None and signos_vitales['saturacion_o2'] < 90:
        return 2, "Saturación O2 < 90% - Requiere atención urgente"
    
    if dolor_eva is not None and dolor_eva >= 8:
        return 2, "Dolor severo (EVA 8-10)"
    
    if via_aerea == 'comprometida':
        return 2, "Vía aérea comprometida"
    
    # Taquicardia/bradicardia severa
    fc = signos_vitales.get('frecuencia_cardiaca')
    if fc is not None and (fc > 150 or fc < 50):
        return 2, f"Frecuencia cardíaca anormal ({fc} lpm)"
    
    # Hipertensión severa
    pas = signos_vitales.get('presion_sistolica')
    if pas is not None and pas > 200:
        return 2, f"Hipertensión severa (PAS {pas} mmHg)"
    
    # ESI 3: Urgencia
    if dolor_eva is not None and dolor_eva >= 4:
        return 3, "Dolor moderado-severo (EVA 4-7)"
    
    # Alteraciones moderadas de signos vitales
    if fc is not None and (fc > 120 or fc < 60):
        return 3, "Frecuencia cardíaca en zona de alerta"
    
    if pas is not None and (pas > 180 or pas < 90):
        return 3, "Presión arterial en zona de alerta"
    
    # ESI 4: Menos urgente
    if dolor_eva is not None and dolor_eva >= 1:
        return 4, "Dolor leve-moderado"
    
    # ESI 5: No urgente (default)
    return 5, "Signos vitales estables, sin urgencia aparente"
