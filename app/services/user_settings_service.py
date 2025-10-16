from dataclasses import dataclass
from typing import Optional, Tuple
from app.models.SettingsModel import calculate_macros, calculate_daily_activity_minutes

@dataclass
class UserSettingsData:
    weight: float
    height: int
    age: int
    gender: str
    activity_level: str  # 'sedentary', 'light', etc.
    goal: str

class UserSettingsService:
    @staticmethod
    def validate_and_process_settings(form_data: dict) -> Tuple[bool, Optional[UserSettingsData], Optional[str]]:
        """Valida y procesa los datos del formulario"""
        try:
            # Validaciones
            weight = float(form_data.get('weight', 0))
            height = int(form_data.get('height', 0))
            age = int(form_data.get('age', 0))
            gender = form_data.get('gender')
            activity_level = form_data.get('activity_level')
            goal = form_data.get('goal')

            # Validaciones de negocio
            if weight <= 0 or height <= 0 or age <= 0:
                return False, None, 'El peso, la altura y la edad deben ser números positivos.'
            
            if weight < 30 or weight > 200:
                return False, None, 'El peso debe estar entre 30 y 200 kg.'
            
            if height < 100 or height > 250:
                return False, None, 'La altura debe estar entre 100 y 250 cm.'
            
            if age < 10 or age > 100:
                return False, None, 'La edad debe estar entre 10 y 100 años.'

            if gender not in ['male', 'female']:
                return False, None, 'Género no válido.'
            
            if activity_level not in ['sedentary', 'light', 'moderate', 'active', 'very_active']:
                return False, None, 'Nivel de actividad no válido.'
            
            if goal not in ['gain', 'lose', 'maintain']:
                return False, None, 'Objetivo no válido.'

            settings_data = UserSettingsData(
                weight=weight,
                height=height,
                age=age,
                gender=gender,
                activity_level=activity_level,
                goal=goal
            )

            return True, settings_data, None

        except (ValueError, TypeError):
            return False, None, 'Por favor, introduce valores numéricos válidos.'

    @staticmethod
    def calculate_user_goals(settings: UserSettingsData) -> dict:
        """Calcula todas las metas del usuario"""
        # Mapeo consistente para cálculos
        activity_for_calculation = {
            'sedentary': 'low',
            'light': 'low', 
            'moderate': 'moderate',
            'active': 'high',
            'very_active': 'high'
        }[settings.activity_level]

        # Cálculos
        calories, proteins, fats, carbs = calculate_macros(
            settings.weight, settings.height, settings.age, 
            settings.gender, activity_for_calculation, settings.goal
        )
        
        activity_minutes = calculate_daily_activity_minutes(
            activity_for_calculation, settings.goal, settings.age
        )

        return {
            'daily_calories': calories,
            'daily_proteins': proteins,
            'daily_fats': fats,
            'daily_carbs': carbs,
            'daily_water': 2.5,  # Podrías calcular esto también
            'daily_activity': activity_minutes
        }