"""
==============================================================================
HARD CONSTRAINTS DATABASE — Límites biológicos inviolables
==============================================================================

Todo agente opera DENTRO de estos límites.
Ningún LLM puede violated: están hard-coded en el motor de simulación.
Si un agente intenta salirse → el Moderator lo rechaza automáticamente.

Cada constraint tiene:
  - key: identificador único
  - min / max: rango biológicamente posible
  - unit: unidad de medida
  - description: por qué existe este límite
  - source: paper o guía clínica de referencia
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import math


@dataclass
class Constraint:
    """Un límite biológico hard-coded."""
    key: str
    min_val: float
    max_val: float
    unit: str
    description: str
    source: str
    severity: str = "critical"  # critical | warning

    def is_valid(self, value: float) -> bool:
        return self.min_val <= value <= self.max_val

    def violation_message(self, value: float) -> str:
        if value < self.min_val:
            return f"{self.key}={value} {self.unit} está por DEBAJO del mínimo biológico ({self.min_val} {self.unit}). {self.description}"
        return f"{self.key}={value} {self.unit} está por ENCIMA del máximo biológico ({self.max_val} {self.unit}). {self.description}"


class HardConstraintsDB:
    """
    Base de datos de límites biológicos.
    Todos los agentes consultan esta DB antes de emitir cualquier señal.
    El Moderatorconsulta esta DB antes de validar cualquier recomendación.
    """

    def __init__(self):
        self._constraints = self._build_constraints()
        self._ranges = self._build_ranges()

    def _build_constraints(self) -> Dict[str, Constraint]:
        """Construye todos los constraints hard-coded."""
        return {

            # ── LÍPIDOS ──────────────────────────────────────────────────
            "ldl_cholesterol": Constraint(
                key="ldl_cholesterol",
                min_val=0.0,
                max_val=400.0,
                unit="mg/dL",
                description="LDL colesterol. Por encima de 400 es hipercolesterolemia familiar severa. Por debajo de 20 es casi imposible biológicamente.",
                source="AHA Guidelines 2023 — ATP-III",
                severity="critical"
            ),
            "hdl_cholesterol": Constraint(
                key="hdl_cholesterol",
                min_val=10.0,
                max_val=120.0,
                unit="mg/dL",
                description="HDL colesterol. Por debajo de 10 es incompatible con vida. Por encima de 120 es hiperalphalipoproteinemia.",
                source="AHA Guidelines 2023",
                severity="critical"
            ),
            "triglycerides": Constraint(
                key="triglycerides",
                min_val=20.0,
                max_val=1000.0,
                unit="mg/dL",
                description="Triglicéridos. Por encima de 1000 riesgo de pancreatitis aguda severo.",
                source="AHA/ACC Guidelines 2023",
                severity="critical"
            ),
            "total_cholesterol": Constraint(
                key="total_cholesterol",
                min_val=50.0,
                max_val=500.0,
                unit="mg/dL",
                description="Colesterol total. Rango clínico completo.",
                source="NCEP ATP-III",
                severity="critical"
            ),

            # ── GLUCOSA ─────────────────────────────────────────────────
            "glucose_fasting": Constraint(
                key="glucose_fasting",
                min_val=40.0,
                max_val=400.0,
                unit="mg/dL",
                description="Glucosa en sangre en ayunas. Por debajo de 40 = hipoglucemia severa con riesgo de pérdida de consciousness. Por encima de 400 = hyperglycemia severa.",
                source="ADA Standards of Care 2024",
                severity="critical"
            ),
            "glucose_post_prandial": Constraint(
                key="glucose_post_prandial",
                min_val=60.0,
                max_val=450.0,
                unit="mg/dL",
                description="Glucosa post-prandial (2h después de comer). Siempre más alta que fasting.",
                source="ADA 2024",
                severity="critical"
            ),
            "hba1c": Constraint(
                key="hba1c",
                min_val=3.5,
                max_val=18.0,
                unit="%",
                description="Hemoglobina glicosilada. Rango clínico de 3.5% (anemia) a 18% (diabetes no controlada severa). Por encima de 14% riesgo de complications severas.",
                source="ADA 2024",
                severity="critical"
            ),
            "insulin_fasting": Constraint(
                key="insulin_fasting",
                min_val=0.5,
                max_val=60.0,
                unit="μIU/mL",
                description="Insulina en ayunas. Por encima de 60 indica resistencia severa a insulina.",
                source="WHO 2024",
                severity="critical"
            ),
            "homa_ir": Constraint(
                key="homa_ir",
                min_val=0.1,
                max_val=25.0,
                unit="",
                description="HOMA-IR. Índice de resistencia a insulina. Por encima de 2.5 = resistencia. Por encima de 10 = severa.",
                source="Matthews 1985 + ADA 2024",
                severity="critical"
            ),

            # ── INFLAMACIÓN ────────────────────────────────────────────
            "c_reactive_protein": Constraint(
                key="c_reactive_protein",
                min_val=0.1,
                max_val=200.0,
                unit="mg/L",
                description="Proteína C reactiva. Rango clínico normal hasta 3 mg/L. Por encima de 10 indica infección o inflamación aguda severa.",
                source="AHA/ACC 2023",
                severity="critical"
            ),
            "ferritin": Constraint(
                key="ferritin",
                min_val=1.0,
                max_val=3000.0,
                unit="ng/mL",
                description="Ferritina. Por encima de 1000 puede indicar storm de hierro o inflammation severa.",
                source="AABB Guidelines + British Society",
                severity="critical"
            ),
            "il6": Constraint(
                key="il6",
                min_val=0.1,
                max_val=500.0,
                unit="pg/mL",
                description="Interleucina-6. En condiciones normales muy baja. Por encima de 100 pg/mL indica cytokine storm.",
                source="Nature Reviews Immunology 2021",
                severity="critical"
            ),
            "fibrinogen": Constraint(
                key="fibrinogen",
                min_val=100.0,
                max_val=1000.0,
                unit="mg/dL",
                description="Fibrinógeno. Por encima de 700 indica inflammation aguda o trombosis.",
                source="CLSI Guidelines",
                severity="critical"
            ),

            # ── FUNCIÓN HEPÁTICA ───────────────────────────────────────
            "alt": Constraint(
                key="alt",
                min_val=0.0,
                max_val=500.0,
                unit="U/L",
                description="ALT (alanina aminotransferasa). Por encima de 500 indica daño hepático agudo severo.",
                source="AASLD Guidelines 2023",
                severity="critical"
            ),
            "ast": Constraint(
                key="ast",
                min_val=0.0,
                max_val=500.0,
                unit="U/L",
                description="AST (aspartato aminotransferasa). Por encima de 500 indica daño hepático o músculo.",
                source="AASLD 2023",
                severity="critical"
            ),
            "ggt": Constraint(
                key="ggt",
                min_val=0.0,
                max_val=1000.0,
                unit="U/L",
                description="Gamma-glutamil transferasa. Por encima de 500 indica cholestasis o daño hepático.",
                source="AASLD 2023",
                severity="critical"
            ),
            "albumin": Constraint(
                key="albumin",
                min_val=1.5,
                max_val=6.0,
                unit="g/dL",
                description="Albúmina sérica. Por debajo de 2.5 indica malnutrición severa o enfermedad hepática descompensada.",
                source="ESPEN Guidelines",
                severity="critical"
            ),

            # ── FUNCIÓN RENAL ──────────────────────────────────────────
            "creatinine_male": Constraint(
                key="creatinine_male",
                min_val=0.3,
                max_val=25.0,
                unit="mg/dL",
                description="Creatinina en hombres. Por encima de 10 indica fallo renal severo.",
                source="KDIGO 2023 Guidelines",
                severity="critical"
            ),
            "creatinine_female": Constraint(
                key="creatinine_female",
                min_val=0.3,
                max_val=20.0,
                unit="mg/dL",
                description="Creatinina en mujeres. Por encima de 8 indica fallo renal severo.",
                source="KDIGO 2023",
                severity="critical"
            ),
            "egfr": Constraint(
                key="egfr",
                min_val=5.0,
                max_val=200.0,
                unit="mL/min/1.73m²",
                description="Tasa de filtrado glomerular estimada. Por debajo de 15 = fallo renal stage 5.",
                source="KDIGO-CKD 2023",
                severity="critical"
            ),
            "urea_bun": Constraint(
                key="urea_bun",
                min_val=2.0,
                max_val=250.0,
                unit="mg/dL",
                description="Nitrógeno ureico en sangre. Por encima de 200 indica uremia severa.",
                source="KDIGO 2023",
                severity="critical"
            ),
            "uric_acid": Constraint(
                key="uric_acid",
                min_val=1.0,
                max_val=20.0,
                unit="mg/dL",
                description="Ácido úrico. Por encima de 13 riesgo de gota severa. Por encima de 15 riesgo de collapse cardiovascular.",
                source="EULAR 2023",
                severity="critical"
            ),

            # ── HORMONAS ──────────────────────────────────────────────
            "tsh": Constraint(
                key="tsh",
                min_val=0.001,
                max_val=100.0,
                unit="mIU/L",
                description="Hormona estimulante del tiroides. Rango clínico非常大: 0.001 (hipertiroidismo severo) a 100 (hipotiroidismo profundo).",
                source="ATA Guidelines 2023",
                severity="critical"
            ),
            "testosterone_male": Constraint(
                key="testosterone_male",
                min_val=10.0,
                max_val=1600.0,
                unit="ng/dL",
                description="Testosterona total en hombres. Por debajo de 100 es hipogonadismo. Por encima de 1500 puede ser tumor.",
                source="Endocrine Society 2023",
                severity="critical"
            ),
            "testosterone_female": Constraint(
                key="testosterone_female",
                min_val=1.0,
                max_val=200.0,
                unit="ng/dL",
                description="Testosterona en mujeres. Por encima de 100 puede indicar SOPCO hirsutismo.",
                source="Endocrine Society",
                severity="critical"
            ),
            "cortisol_morning": Constraint(
                key="cortisol_morning",
                min_val=1.0,
                max_val=60.0,
                unit="μg/dL",
                description="Cortisol matutino (8-9am). Por encima de 30 indica Cushing. Por debajo de 5 indica Addison.",
                source="Endocrine Society 2023",
                severity="critical"
            ),
            "dhea_s": Constraint(
                key="dhea_s",
                min_val=5.0,
                max_val=1500.0,
                unit="μg/dL",
                description="DHEA-S (sulfato de DHEA). Por debajo de 20 en adultos jóvenes puede indicar adrenal insufficiency.",
                source="Endocrine Society 2023",
                severity="critical"
            ),
            "estradiol_male": Constraint(
                key="estradiol_male",
                min_val=5.0,
                max_val=100.0,
                unit="pg/mL",
                description="Estradiol en hombres. Por encima de 60 puede indicar feminización o tumor.",
                source="Endocrine Society",
                severity="critical"
            ),
            "free_t3": Constraint(
                key="free_t3",
                min_val=0.5,
                max_val=15.0,
                unit="pg/mL",
                description="T3 libre. Por debajo de 1.5 hipotiroidismo severo. Por encima de 10 hipertiroidismo.",
                source="ATA 2023",
                severity="critical"
            ),
            "free_t4": Constraint(
                key="free_t4",
                min_val=0.1,
                max_val=8.0,
                unit="ng/dL",
                description="T4 libre. Por debajo de 0.5 hipotiroidismo severo.",
                source="ATA 2023",
                severity="critical"
            ),

            # ── NUTRICIONAL ───────────────────────────────────────────
            "vitamin_d": Constraint(
                key="vitamin_d",
                min_val=3.0,
                max_val=200.0,
                unit="ng/mL",
                description="Vitamina D (25-OH). Por encima de 150 es toxicidad. Por debajo de 10 = deficiencia severa con raquitismo/osteomalacia.",
                source="Endocrine Society 2023",
                severity="critical"
            ),
            "vitamin_b12": Constraint(
                key="vitamin_b12",
                min_val=50.0,
                max_val=2000.0,
                unit="pg/mL",
                description="Vitamina B12. Por debajo de 150 es deficiencia. Por encima de 1500 puede indicar enfermedad myeloproliferativa.",
                source="British Society Haematology 2023",
                severity="critical"
            ),
            "folate_rbc": Constraint(
                key="folate_rbc",
                min_val=50.0,
                max_val=1500.0,
                unit="ng/mL",
                description="Folato en glóbulos rojos. Por debajo de 150 indica deficiencia.",
                source="WHO 2023",
                severity="critical"
            ),
            "homocysteine": Constraint(
                key="homocysteine",
                min_val=2.0,
                max_val=100.0,
                unit="μmol/L",
                description="Homocisteína. Por encima de 50 indica defect de B12 o folato severo o problema renal.",
                source="AHA 2023",
                severity="critical"
            ),
            "iron": Constraint(
                key="iron",
                min_val=10.0,
                max_val=400.0,
                unit="μg/dL",
                description="Hierro sérico. Por encima de 300 puede indicar hemocromatosis o loading de hierro.",
                source="AABB 2023",
                severity="critical"
            ),
            "transferrin_saturation": Constraint(
                key="transferrin_saturation",
                min_val=5.0,
                max_val=100.0,
                unit="%",
                description="Saturación de transferrina. Por encima de 45% indica iron overload. Por debajo de 15% indica deficiency.",
                source="AABB/WHO",
                severity="critical"
            ),

            # ── SISTEMA INMUNE ─────────────────────────────────────────
            "leukocytes": Constraint(
                key="leukocytes",
                min_val=500.0,
                max_val=100000.0,
                unit="cells/μL",
                description="Leucocitos totales. Por debajo de 1000 = severe leukopenia con alto riesgo de infection. Por encima de 50000 = leukemia o infection severa.",
                source="CLSI/Henry's Clinical Diagnosis 2023",
                severity="critical"
            ),
            "lymphocytes_pct": Constraint(
                key="lymphocytes_pct",
                min_val=1.0,
                max_val=80.0,
                unit="%",
                description="Linfocitos como porcentaje de leucocitos. Por debajo de 5% indica immunocompromiso severo.",
                source="CLSI",
                severity="critical"
            ),
            "iga": Constraint(
                key="iga",
                min_val=5.0,
                max_val=600.0,
                unit="mg/dL",
                description="Inmunoglobulina A. Por debajo de 5 deficiencia total. Por encima de 600 gamopatía monoclonal.",
                source="UIS EAACI Guidelines",
                severity="critical"
            ),
            "igg": Constraint(
                key="igg",
                min_val=100.0,
                max_val=4000.0,
                unit="mg/dL",
                description="Inmunoglobulina G. Por debajo de 200 indica immunodeficiency. Por encima de 3000 indica gamopatía.",
                source="UIS EAACI",
                severity="critical"
            ),

            # ── FUNCIÓN COGNITIVA / NEUROLÓGICO ───────────────────────
            "ldl_oxidation_risk": Constraint(
                key="ldl_oxidation_risk",
                min_val=0.0,
                max_val=1.0,
                unit="",
                description="Riesgo de oxidación LDL (0-1 score). score > 0.7 indica LDL altamente oxidado y aterogénico. Biológicamente el máximo es 1.0.",
                source="AHA Journal 2022",
                severity="critical"
            ),

            # ── PRESIÓN ARTERIAL ──────────────────────────────────────
            "systolic_bp": Constraint(
                key="systolic_bp",
                min_val=60.0,
                max_val=300.0,
                unit="mmHg",
                description="Presión arterial sistólica. Por encima de 250 crisis hipertensiva con riesgo de stroke. Por debajo de 70 shock.",
                source="ACC/AHA 2023 Hypertension Guidelines",
                severity="critical"
            ),
            "diastolic_bp": Constraint(
                key="diastolic_bp",
                min_val=30.0,
                max_val=200.0,
                unit="mmHg",
                description="Presión arterial diastólica. Por encima de 150 crisis. Por debajo de 30 hypotension severa.",
                source="ACC/AHA 2023",
                severity="critical"
            ),

            # ── FRECUENCIA CARDÍACA ───────────────────────────────────
            "hr_resting": Constraint(
                key="hr_resting",
                min_val=25.0,
                max_val=220.0,
                unit="bpm",
                description="Frecuencia cardíaca en reposo. Por encima de 180 tachycardia severa. Por debajo de 30 bradycardia sintomática.",
                source="AHA/ACC 2023",
                severity="critical"
            ),

            # ── PESO / COMPOSICIÓN CORPORAL ──────────────────────────
            "bmi": Constraint(
                key="bmi",
                min_val=10.0,
                max_val=80.0,
                unit="kg/m²",
                description="Índice de masa corporal. Por encima de 70 es obesidad mórbida. Por debajo de 12 es malnutrición severa.",
                source="WHO Obesity Guidelines 2023",
                severity="critical"
            ),
            "waist_circumference_male": Constraint(
                key="waist_circumference_male",
                min_val=50.0,
                max_val=200.0,
                unit="cm",
                description="Perímetro de cintura en hombres. Por encima de 127 cm riesgo metabólico muy alto.",
                source="IDF/NHLBI Criteria",
                severity="critical"
            ),
            "waist_circumference_female": Constraint(
                key="waist_circumference_female",
                min_val=45.0,
                max_val=200.0,
                unit="cm",
                description="Perímetro de cintura en mujeres. Por encima de 112 cm riesgo metabólico muy alto.",
                source="IDF/NHLBI",
                severity="critical"
            ),
            "body_fat_pct_male": Constraint(
                key="body_fat_pct_male",
                min_val=3.0,
                max_val=70.0,
                unit="%",
                description="Porcentaje de grasa corporal en hombres. Por debajo de 3% es esencial body fat mínimo. Por encima de 60% es obesidad severa.",
                source="ACSM Guidelines",
                severity="critical"
            ),
            "body_fat_pct_female": Constraint(
                key="body_fat_pct_female",
                min_val=8.0,
                max_val=70.0,
                unit="%",
                description="Porcentaje de grasa corporal en mujeres. Por debajo de 8% dysfunction hormonal. Por encima de 60% obesidad severa.",
                source="ACSM",
                severity="critical"
            ),

            # ── VO2MAX / RENDIMIENTO ──────────────────────────────────
            "vo2max": Constraint(
                key="vo2max",
                min_val=5.0,
                max_val=95.0,
                unit="mL/kg/min",
                description="Consumo máximo de oxígeno. El máximo biológico posible ~95 mL/kg/min (atletas elite). Por debajo de 15 limitaciones funcionales severas.",
                source="ACSM / European Journal of Applied Physiology",
                severity="critical"
            ),
            "hrv_sdnn": Constraint(
                key="hrv_sdnn",
                min_val=5.0,
                max_val=300.0,
                unit="ms",
                description="SDNN (desviación estándar de NN intervals) como marcador de HRV. Por encima de 150 indica recovery excelente. Por debajo de 20 indica estrés severo.",
                source="ESC Guidelines on HRV 2023",
                severity="warning"
            ),

            # ── CETONAS / METABOLISMO FLEXIBILIDAD ────────────────────
            "beta_hydroxybutyrate": Constraint(
                key="beta_hydroxybutyrate",
                min_val=0.0,
                max_val=10.0,
                unit="mmol/L",
                description="Betahidroxibutirato (cuerpo cetónicos). Por encima de 3.0 mmol/L = nutricional ketosis. Por encima de 5 = fasting ketosis profunda.",
                source="Volek & Phinney — The Art and Science of Low-Carb Living",
                severity="critical"
            ),
            "respiratory_quotient": Constraint(
                key="respiratory_quotient",
                min_val=0.65,
                max_val=1.30,
                unit="",
                description="Coeficiente respiratorio (RQ = VCO2/VO2). 0.7 = oxidación pura de grasa. 1.0 = oxidación pura de glucosa. Por encima de 1.0 indica lipogenesis activa o hyperventilación.",
                source="J. G. Webster — Metabolic Systems",
                severity="warning"
            ),

            # ── MOLÉCULAR / LONGEVIDAD ────────────────────────────────
            "nadi_level": Constraint(
                key="nadi_level",
                min_val=10.0,
                max_val=200.0,
                unit="%",
                description="Niveles de NAD+ en porcentaje del valor máximo. Disminuye ~10% por década después de los 40. Por debajo de 30% riesgo de mitochondrial dysfunction severa.",
                source="Dellinger & Baur Labs / Cell 2017 (Zhang et al.)",
                severity="critical"
            ),
            "ampk_activity": Constraint(
                key="ampk_activity",
                min_val=10.0,
                max_val=300.0,
                unit="%",
                description="Actividad de AMPK como porcentaje. Activado por ayuno y ejercicio. Por debajo de 20% indica metabolic inflexibility severa.",
                source="Carling et al. — AMPK: a master regulator of metabolic health",
                severity="critical"
            ),
            "mtor_activity": Constraint(
                key="mtor_activity",
                min_val=5.0,
                max_val=200.0,
                unit="%",
                description="Actividad de mTOR como porcentaje. Activado por aminoácids y growth factors. Inhibition por debajo de 20% indica autofagia activa. Por encima de 150% indica anabolismo excesivo.",
                source="Saxton & Sabatini — mTOR Signaling in Growth and Disease",
                severity="critical"
            ),
            "autophagy_marker": Constraint(
                key="autophagy_marker",
                min_val=0.0,
                max_val=100.0,
                unit="%",
                description="Marcador de autofagia activa (0-100). Se activa con ayuno > 16h, ejercicio intenso, y ciertos compuestos (spermidine). Por encima de 80% indica fasting profundo.",
                source="Mizushima & Levine — Autophagy in human disease",
                severity="warning"
            ),
            "telomere_length": Constraint(
                key="telomere_length",
                min_val=3000.0,
                max_val=15000.0,
                unit="bp",
                description="Longitud de telómeros en pares de bases. Por debajo de 5000 bp asociado a diseases del envejecimiento. Por encima de 12000 bp encontrado en centenario.",
                source="Aging Cell 2022 — telomere length reference ranges",
                severity="critical"
            ),

            # ── IMC/metabólicos ───────────────────────────────────────
            "basal_metabolic_rate": Constraint(
                key="basal_metabolic_rate",
                min_val=500.0,
                max_val=6000.0,
                unit="kcal/day",
                description="Tasa metabólica basal. Por debajo de 800 imposible sin malnutrition severa. Por encima de 5000 solo en hombres muy grandes y activos.",
                source="Mifflin-St Jeor Equation / Henry 2005",
                severity="critical"
            ),
            "thermal_effect_food": Constraint(
                key="thermal_effect_food",
                min_val=5.0,
                max_val=30.0,
                unit="%",
                description="Efecto termogénico de los alimentos (TEF). Por encima de 25% solo en high-protein diets. Por debajo de 7% indica metabolic dysfunction.",
                source="Westerterp — Diet-induced thermogenesis",
                severity="warning"
            ),

            # ── SUEÑO ──────────────────────────────────────────────────
            "sleep_hours": Constraint(
                key="sleep_hours",
                min_val=0.0,
                max_val=24.0,
                unit="h",
                description="Horas de sueño. Por encima de 20 horas puede indicar narcolepsia o condition médica. Por debajo de 2 es supervivencia.",
                source="AASM Guidelines 2023",
                severity="critical"
            ),
            "sleep_efficiency": Constraint(
                key="sleep_efficiency",
                min_val=0.0,
                max_val=100.0,
                unit="%",
                description="Eficiencia del sueño (time asleep / time in bed × 100). Por encima de 95% inusualmente alto. Por debajo de 50% indica insomnia severa.",
                source="AASM 2023",
                severity="critical"
            ),
            "cortisol_wake_up": Constraint(
                key="cortisol_wake_up",
                min_val=3.0,
                max_val=40.0,
                unit="μg/dL",
                description="Cortisol al despertar (Cortisol Awakening Response). Por debajo de 5 indica HPA axis dysregulation. Por encima de 30 indica estrés crónico.",
                source="Stalder et al. — Cortisol Awakening Response 2016",
                severity="warning"
            ),

            # ── EDADES BIOLÓGICAS ─────────────────────────────────────
            "biological_age_phenotype": Constraint(
                key="biological_age_phenotype",
                min_val=0.0,
                max_val=120.0,
                unit="years",
                description="Edad fenotípica (PhenoAge). Puede ser mayor que chronological age sin límite superior, pero biológicamente no más de 120 años.",
                source="Levine et al. 2018 — PNAS",
                severity="critical"
            ),
            "age_acceleration": Constraint(
                key="age_acceleration",
                min_val=-30.0,
                max_val=50.0,
                unit="years",
                description="Diferencia entre edad biológica y cronológica. Por encima de 30 años de aceleración indica enfermedad grave. Por debajo de -10 es outliers excepcionales.",
                source="DunedinPACE — Belsky et al. 2022",
                severity="warning"
            ),
            "dunelpace": Constraint(
                key="dunelpace",
                min_val=0.5,
                max_val=2.5,
                unit="",
                description="DunedinPACE score. 1.0 = ritmo de envejecimiento promedio. Por encima de 1.5 envejecimiento acelerado. Por debajo de 0.7 envejecimiento decelerado (centenarios).",
                source="Belsky et al. 2022 — eLife",
                severity="critical"
            ),
        }

    def _build_ranges(self) -> Dict[str, Dict[str, Any]]:
        """Construye rangos normales y de riesgo por biomarcador."""
        return {
            # Lípidos (mg/dL)
            "ldl_cholesterol": {
                "optimal": (0, 100),
                "near_optimal": (100, 130),
                "borderline": (130, 160),
                "high": (160, 190),
                "very_high": (190, 400),
            },
            "hdl_cholesterol": {
                "low_risk": (60, 120),
                "moderate_risk": (40, 60),
                "high_risk": (10, 40),
            },
            "triglycerides": {
                "normal": (20, 150),
                "borderline": (150, 200),
                "high": (200, 500),
                "very_high": (500, 1000),
            },
            "glucose_fasting": {
                "normal": (70, 99),
                "prediabetes": (100, 125),
                "diabetes": (126, 400),
                "hypoglycemia": (40, 70),
            },
            "hba1c": {
                "normal": (4.0, 5.6),
                "prediabetes": (5.7, 6.4),
                "diabetes": (6.5, 18.0),
            },
            "c_reactive_protein": {
                "low_risk": (0.1, 1.0),
                "moderate_risk": (1.0, 3.0),
                "high_risk": (3.0, 10.0),
                "acute_inflammation": (10.0, 200.0),
            },
            "homocysteine": {
                "optimal": (2.0, 10.0),
                "moderate_risk": (10.0, 15.0),
                "high_risk": (15.0, 30.0),
                "very_high_risk": (30.0, 100.0),
            },
            "vitamin_d": {
                "deficiency": (3.0, 20.0),
                "insufficiency": (20.0, 30.0),
                "sufficiency": (30.0, 100.0),
                "potential_toxicity": (100.0, 200.0),
            },
            "homa_ir": {
                "sensitive": (0.1, 1.0),
                "normal": (1.0, 2.5),
                "resistance": (2.5, 5.0),
                "severe_resistance": (5.0, 25.0),
            },
            "egfr": {
                "normal": (90, 200),
                "mild_ckd": (60, 90),
                "moderate_ckd": (45, 60),
                "severe_ckd": (30, 45),
                "kidney_failure": (5, 30),
            },
            "vo2max": {
                "poor": (5.0, 25.0),
                "fair": (25.0, 35.0),
                "good": (35.0, 45.0),
                "excellent": (45.0, 60.0),
                "elite": (60.0, 95.0),
            },
        }

    # ── MÉTODOS DE CONSULTA ─────────────────────────────────────────────

    def validate(self, key: str, value: float) -> tuple[bool, str]:
        """
        Valida un valor contra el constraint hard-coded.
        Returns: (is_valid: bool, message: str)
        """
        if key not in self._constraints:
            return True, f"Key '{key}' no tiene constraint hard-coded — saltando validación."

        c = self._constraints[key]
        if c.is_valid(value):
            return True, ""
        return False, c.violation_message(value)

    def validate_all(self, data: Dict[str, float]) -> Dict[str, str]:
        """Valida un dictionary completo de biomarcadores. Returns dict de errores."""
        errors = {}
        for key, value in data.items():
            is_valid, msg = self.validate(key, value)
            if not is_valid:
                errors[key] = msg
        return errors

    def is_in_range(self, key: str, value: float, range_name: str) -> bool:
        """Check si un valor está dentro de un rango específico (ej: 'optimal', 'high_risk')."""
        if key not in self._ranges:
            return False
        range_info = self._ranges[key]
        if range_name not in range_info:
            return False
        lo, hi = range_info[range_name]
        return lo <= value <= hi

    def get_risk_level(self, key: str, value: float) -> str:
        """Devuelve el nivel de riesgo clínico para un biomarcador."""
        if key not in self._ranges:
            return "unknown"
        for level_name, (lo, hi) in self._ranges[key].items():
            if lo <= value <= hi:
                return level_name
        return "out_of_range"

    def check_biological_plausibility(self, agent_output: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        Verifica si las acciones/outputs de un agente son biológicamente plausibles.
        Called por el Moderator antes de aprobar recomendaciones.
        """
        violations = []
        biomarkers = agent_output.get("biomarkers", {})

        for key, value in biomarkers.items():
            is_valid, msg = self.validate(key, value)
            if not is_valid:
                violations.append(f"VIOLATION [{agent_output.get('agent','unknown')}]: {msg}")

        return len(violations) == 0, violations

    def get_constraint(self, key: str) -> Optional[Constraint]:
        return self._constraints.get(key)


# Singleton
constraints_db = HardConstraintsDB()