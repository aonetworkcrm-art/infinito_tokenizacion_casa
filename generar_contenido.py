#!/usr/bin/env python3
"""
generar_contenido.py — Generador Automático de Contenido SEO
=============================================================
Proyecto Infinito · Nicho: Abogados de Accidentes (Personal Injury)
CPC: $150-$300 | Promedio: $220

Genera 5 artículos HTML optimizados para SEO con:
  - Meta tags (title, description, keywords, Open Graph)
  - Estructura H1-H3 semántica
  - FAQ Schema JSON-LD
  - Estilo Matrix del Proyecto Infinito
  - Listo para deploy en Netlify/GitHub Pages

Uso:
    python generar_contenido.py
    
    Genera 5 archivos .html en ./contenido/
    
    python generar_contenido.py --all
    
    Genera los 12 artículos del nicho completo
"""

import os
import json
import argparse
from datetime import datetime
from typing import List, Dict


# ─── DATOS DE LOS ARTÍCULOS ───────────────────────────────────────────────

ARTICULOS = [
    {
        "id": "guia-abogados-accidentes",
        "slug": "guia-abogados-accidentes",
        "title": "Guía Completa de Abogados de Accidentes: Todo lo que Necesitas Saber en 2026",
        "meta_desc": "Guía completa sobre abogados de accidentes. Tipos de casos, costos, calculadora de indemnización y pasos a seguir. Consulta gratis.",
        "keywords": "abogado de accidentes, personal injury attorney, car accident lawyer near me, abogado lesiones personales, consulta gratis abogado accidente",
        "h1": "Guía Completa de Abogados de Accidentes [2026]",
        "intro": "Sufrir un accidente puede ser una de las experiencias más abrumadoras en la vida de una persona. Entre las facturas médicas que se acumulan, los días de trabajo perdidos y el estrés emocional, saber qué hacer y a quién recurrir marca una diferencia monumental en el resultado de tu caso. Esta guía ha sido creada para ayudarte a entender todo lo que necesitas saber sobre los abogados de accidentes, cómo funcionan, cuánto cuestan y cómo elegir al mejor para tu situación.",
        "sections": [
            {
                "h2": "¿Cuándo Necesitas un Abogado de Accidentes?",
                "content": "No todos los accidentes requieren representación legal, pero hay situaciones donde contratar un abogado no solo es recomendable, sino necesario. Si has sufrido lesiones que requieren tratamiento médico continuo, si el seguro te ofrece una cantidad muy por debajo de lo que necesitas, o si hay disputa sobre quién tuvo la culpa, un abogado especializado puede marcar la diferencia entre una compensación justa y quedarse con nada.",
                "list": [
                    "Lesiones graves que requieren hospitalización o cirugía",
                    "Disputas sobre responsabilidad (quién causó el accidente)",
                    "Ofertas de liquidación bajas por parte de las aseguradoras",
                    "Accidentes que involucran múltiples partes",
                    "Cuando el conductor no tiene seguro o tiene seguro insuficiente"
                ]
            },
            {
                "h2": "Tipos de Accidentes que Cubrimos",
                "content": "Los abogados de lesiones personales manejan una amplia variedad de casos. Cada tipo de accidente tiene sus propias complejidades legales y estratégicas. A continuación, desglosamos los casos más comunes:",
                "subsections": [
                    {
                        "h3": "Accidentes de Auto",
                        "content": "Los accidentes automovilísticos son la causa más común de lesiones personales. Según la NHTSA, ocurren más de 6 millones de accidentes de auto al año solo en Estados Unidos. Un abogado especializado puede ayudarte a navegar el complejo mundo de las reclamaciones al seguro, determinar responsabilidad y maximizar tu compensación."
                    },
                    {
                        "h3": "Accidentes de Camiones (18 Ruedas)",
                        "content": "Los accidentes con camiones de carga son particularmente devastadores debido al peso y tamaño de estos vehículos. Estos casos involucran regulaciones federales (FMCSA), múltiples responsables (conductor, empresa de transporte, fabricante) y seguros comerciales con límites mucho más altos."
                    },
                    {
                        "h3": "Accidentes de Motocicleta",
                        "content": "Los motociclistas tienen 28 veces más probabilidades de morir en un accidente que los ocupantes de un automóvil. Además, existe un sesgo injusto contra los motociclistas en los tribunales. Un abogado con experiencia en accidentes de moto sabe cómo contrarrestar estos prejuicios."
                    },
                    {
                        "h3": "Resbalones y Caídas",
                        "content": "Las propiedades comerciales y residenciales tienen la obligación legal de mantener sus instalaciones seguras. Si te has lesionado debido a condiciones peligrosas como pisos mojados sin señalización, pasillos mal iluminados o superficies irregulares, podrías tener derecho a compensación."
                    },
                    {
                        "h3": "Muerte por Negligencia",
                        "content": "Cuando una persona fallece debido a la negligencia de otro, los familiares pueden presentar una demanda por muerte por negligencia. Esta compensación cubre gastos funerarios, pérdida de ingresos futuros, y el dolor emocional de perder a un ser querido."
                    }
                ]
            },
            {
                "h2": "¿Cuánto Cuesta un Abogado de Accidentes?",
                "content": "La mayoría de los abogados de lesiones personales trabajan bajo un modelo de honorarios de contingencia. Esto significa que no pagas nada por adelantado. El abogado recibe un porcentaje de la compensación solo si gana tu caso. Típicamente, este porcentaje oscila entre el 25% y el 40%, dependiendo de la complejidad del caso y si el caso llega a juicio.",
                "list": [
                    "Consulta inicial: 100% gratuita",
                    "Honorarios de contingencia: 25%-40% (solo si ganas)",
                    "Sin ganancia = sin honorarios legales",
                    "Costos administrativos (forenses, peritos): se descuentan del acuerdo"
                ]
            },
            {
                "h2": "Pasos a Seguir Después de un Accidente",
                "content": "Lo que hagas en los minutos, horas y días posteriores a un accidente puede tener un impacto significativo en tu caso. Sigue estos pasos para proteger tus derechos:",
                "numbered": [
                    "Busca atención médica inmediata, incluso si no sientes dolor (las lesiones pueden manifestarse horas o días después)",
                    "Documenta la escena: fotos, videos, testigos, número de placas",
                    "No admitas culpa, ni siquiera disculpas educadas",
                    "Reporta el accidente a las autoridades y obtén una copia del informe",
                    "Notifica a tu seguro, pero NO des una declaración grabada sin tu abogado presente",
                    "Contacta a un abogado de accidentes antes de aceptar cualquier oferta",
                    "Guarda todos los registros médicos, facturas y comprobantes de gastos"
                ]
            },
            {
                "h2": "¿Cuánto Vale mi Caso? Factores Clave",
                "content": "El valor de un caso de lesiones personales depende de múltiples factores. No hay dos casos iguales, pero los siguientes elementos son los más importantes para determinar la compensación:",
                "list": [
                    "Gravedad de las lesiones y tiempo de recuperación",
                    "Costos médicos totales (actuales y futuros)",
                    "Pérdida de ingresos y capacidad de generar ingresos",
                    "Daños no económicos: dolor y sufrimiento, pérdida de calidad de vida",
                    "Porcentaje de culpa asignado (comparative negligence)",
                    "Límites de las pólizas de seguro disponibles"
                ]
            }
        ],
        "faqs": [
            {
                "question": "¿Cuánto tiempo tengo para demandar después de un accidente?",
                "answer": "El plazo de prescripción (statute of limitations) varía según el estado y el tipo de caso. En la mayoría de los estados, tienes entre 1 y 3 años desde la fecha del accidente para presentar una demanda. Sin embargo, hay excepciones. Lo mejor es contactar a un abogado lo antes posible para no perder tu derecho a reclamar."
            },
            {
                "question": "¿Qué pasa si el accidente fue parcialmente mi culpa?",
                "answer": "Depende del estado donde ocurrió el accidente. En estados con culpa comparativa pura, puedes recuperar daños incluso si eres 99% culpable (aunque reducido proporcionalmente). En estados con culpa comparativa modificada, generalmente necesitas ser menos del 50% o 51% culpable para recuperar algo. En estados con culpa contributiva pura, si tienes cualquier grado de culpa, no puedes recuperar nada."
            },
            {
                "question": "¿Debo hablar con la aseguradora antes de contratar un abogado?",
                "answer": "No. Las aseguradoras tienen equipos de ajustadores entrenados para minimizar los pagos. Todo lo que digas puede ser usado en tu contra. Lo más recomendable es no dar declaraciones grabadas ni firmar nada hasta que tu abogado revise los documentos. Ellos pueden decir 'no' por ti mientras protegen tus derechos."
            },
            {
                "question": "¿Cuánto tiempo toma resolver un caso de lesiones personales?",
                "answer": "El tiempo varía según la complejidad del caso. Los casos simples pueden resolverse en 3-6 meses mediante acuerdo. Los casos más complejos que requieren litigio pueden tomar de 1 a 3 años. Factores como la gravedad de las lesiones, la cooperación de las aseguradoras y la carga del tribunal influyen en la duración."
            },
            {
                "question": "¿Puedo cambiar de abogado si no estoy satisfecho?",
                "answer": "Sí, tienes derecho a cambiar de abogado en cualquier momento. Sin embargo, el abogado original puede tener derecho a un 'privilegio de retención' sobre los honorarios por el trabajo realizado hasta ese momento. Es importante revisar tu contrato de representación y comunicar claramente tus razones para el cambio."
            },
            {
                "question": "¿Qué debo llevar a mi primera consulta con un abogado?",
                "answer": "Lleva toda la documentación relacionada con el accidente: informe policial, fotos de la escena y las lesiones, registros médicos y facturas, información del seguro, comprobantes de pérdida de ingresos, y cualquier comunicación que hayas tenido con las aseguradoras. Entre más información tengas, mejor podrá evaluar tu caso el abogado."
            }
        ]
    },
    {
        "id": "calculadora-indemnizacion",
        "slug": "calculadora-indemnizacion-accidente",
        "title": "Calculadora de Indemnización por Accidente: ¿Cuánto Vale tu Caso?",
        "meta_desc": "Calcula el valor estimado de tu caso de accidente. Factores: lesiones, costos médicos, pérdida de ingresos. Obtén una evaluación gratuita.",
        "keywords": "calculadora indemnización accidente, settlement calculator, cuánto vale mi caso, personal injury settlement calculator, valoración lesiones",
        "h1": "Calculadora de Indemnización por Accidente",
        "intro": "Una de las preguntas más frecuentes después de sufrir un accidente es: ¿cuánto vale mi caso? Aunque cada caso es único y solo un abogado puede darte una evaluación precisa, esta calculadora te dará una estimación basada en los factores más comunes que determinan el valor de una reclamación por lesiones personales.",
        "sections": [
            {
                "h2": "¿Cómo se Calcula una Indemnización por Accidente?",
                "content": "El valor de un caso de lesiones personales se compone de dos categorías principales de daños: económicos y no económicos. Los daños económicos son aquellos que tienen un valor monetario directo y están respaldados por facturas y recibos. Los daños no económicos son más subjetivos y compensan el dolor y el sufrimiento experimentado.",
                "subsections": [
                    {
                        "h3": "Daños Económicos (Tangibles)",
                        "content": "Incluyen gastos médicos pasados y futuros, pérdida de ingresos, pérdida de capacidad de generar ingresos, daños a la propiedad, y gastos de bolsillo relacionados con el accidente (transporte, medicamentos, cuidados en el hogar)."
                    },
                    {
                        "h3": "Daños No Económicos (Intangibles)",
                        "content": "Compensan el dolor físico, el sufrimiento emocional, la pérdida de disfrute de la vida, la desfiguración, la discapacidad permanente, y la pérdida de relación conyugal. Generalmente se calculan como un múltiplo de los daños económicos (entre 1.5x y 5x)."
                    }
                ]
            },
            {
                "h2": "Factores que Aumentan el Valor de tu Indemnización",
                "content": "Ciertos factores pueden aumentar significativamente el valor de tu caso. Los abogados expertos saben cómo identificar y argumentar estos elementos para maximizar tu compensación.",
                "list": [
                    "Lesiones permanentes o discapacidad a largo plazo",
                    "Cirugías o procedimientos invasivos requeridos",
                    "Impacto significativo en tu calidad de vida",
                    "Claridad en la responsabilidad del otro conductor",
                    "Documentación médica exhaustiva y consistente",
                    "Testigos independientes que respalden tu versión"
                ]
            },
            {
                "h2": "Casos Reales: Rangos de Indemnización",
                "content": "Para darte una idea más concreta, aquí presentamos rangos de indemnización basados en casos reales anonimizados. Recuerda que cada caso es único y estos números son solo referenciales.",
                "list": [
                    "Lesiones leves (latigazo cervical, contusiones): $5,000 - $25,000",
                    "Lesiones moderadas (fracturas, esguinces graves): $25,000 - $100,000",
                    "Lesiones graves (cirugía, discapacidad parcial): $100,000 - $500,000",
                    "Lesiones catastróficas (parálisis, daño cerebral): $500,000 - $5,000,000+",
                    "Muerte por negligencia: $1,000,000 - $10,000,000+"
                ]
            }
        ],
        "faqs": [
            {
                "question": "¿Qué tan precisa es esta calculadora de indemnización?",
                "answer": "Esta calculadora te da una estimación preliminar basada en factores comunes. No reemplaza una evaluación legal completa. Cada caso tiene matices únicos que solo un abogado experimentado puede evaluar correctamente."
            },
            {
                "question": "¿Cómo se calculan los daños por dolor y sufrimiento?",
                "answer": "El método más común es el 'multiplicador': se toman los daños económicos totales y se multiplican por un factor entre 1.5 y 5, dependiendo de la gravedad de las lesiones. Algunos abogados usan el método de 'tarifa diaria' asignando un valor a cada día que la víctima sufre."
            },
            {
                "question": "¿Las ofertas iniciales del seguro son justas?",
                "answer": "Generalmente no. Las primeras ofertas de las aseguradoras suelen ser significativamente más bajas de lo que el caso realmente vale. Nunca aceptes la primera oferta sin consultar a un abogado."
            }
        ]
    },
    {
        "id": "accidente-camion-guia",
        "slug": "accidente-camion-guia-legal",
        "title": "Accidente de Camión: Guía Legal Completa para Víctimas y Familias",
        "meta_desc": "Guía legal para víctimas de accidentes de camión. Responsabilidad, compensación, plazos legales. Consulta especializada gratuita.",
        "keywords": "abogado accidentes camiones, truck accident lawyer, accidente camión guía legal, compensación accidente trailer, FMCSA regulations",
        "h1": "Accidente de Camión: Guía Legal para Víctimas y Familias",
        "intro": "Los accidentes que involucran camiones de carga son radicalmente diferentes a los accidentes entre automóviles. El peso de un camión completamente cargado puede superar las 80,000 libras, comparado con las 4,000 libras de un auto promedio. Esta diferencia de masa significa que las lesiones suelen ser mucho más graves y los casos legalmente más complejos. Esta guía te explicará todo lo que necesitas saber si tú o un ser querido han estado involucrados en un accidente de camión.",
        "sections": [
            {
                "h2": "Por qué los Accidentes de Camión son Diferentes",
                "content": "Los accidentes con camiones no solo son más devastadores físicamente, sino que también son legalmente más complejos. A diferencia de un accidente entre dos autos, los accidentes de camión involucran regulaciones federales, múltiples partes potencialmente responsables, y seguros comerciales con dinámicas muy diferentes.",
                "list": [
                    "Regulaciones federales de la FMCSA (Federal Motor Carrier Safety Administration)",
                    "Límites de horas de conducción y registros de horas de servicio",
                    "Mantenimiento obligatorio y registros de inspección",
                    "Responsabilidad compartida entre conductor, empresa y fabricante",
                    "Seguros comerciales con límites de $750,000 a $5,000,000"
                ]
            },
            {
                "h2": "¿Quién es Responsable en un Accidente de Camión?",
                "content": "Una característica única de los accidentes de camión es que puede haber múltiples partes responsables. Identificar a todas las partes responsables es crucial para maximizar la compensación.",
                "subsections": [
                    {
                        "h3": "El Conductor del Camión",
                        "content": "Si el conductor estaba fatigado, bajo la influencia de sustancias, o violando las regulaciones de horas de servicio, puede ser considerado responsable. Sin embargo, los conductores suelen tener recursos limitados."
                    },
                    {
                        "h3": "La Empresa de Transporte",
                        "content": "La compañía para la que trabaja el conductor puede ser responsable bajo la doctrina de 'respondent superior' (responsabilidad del empleador). Además, si la empresa no mantuvo adecuadamente el camión o presionó al conductor a violar regulaciones, tiene responsabilidad directa."
                    },
                    {
                        "h3": "El Fabricante del Camión",
                        "content": "Si un defecto de diseño o fabricación en el camión contribuyó al accidente (fallo de frenos, desprendimiento de rueda, problemas de dirección), el fabricante puede ser responsable bajo la ley de responsabilidad del producto."
                    },
                    {
                        "h3": "Otras Partes",
                        "content": "Dependiendo de las circunstancias, otras partes como los cargadores de la carga, empresas de mantenimiento externas, o incluso entidades gubernamentales responsables del mantenimiento de la carretera podrían tener algún grado de responsabilidad."
                    }
                ]
            },
            {
                "h2": "Pasos Inmediatos Después de un Accidente de Camión",
                "content": "Debido a la complejidad de estos casos, los pasos que tomes inmediatamente después del accidente son aún más críticos que en un accidente regular.",
                "numbered": [
                    "Busca atención médica de emergencia — las lesiones internas pueden no ser evidentes de inmediato",
                    "Llama a la policía — el informe oficial es crucial, especialmente porque documentará las violaciones regulatorias",
                    "Toma fotos y videos de todo: daños, posición de los vehículos, condiciones de la carretera, placas, números DOT del camión",
                    "Obtén información de testigos independientes",
                    "NO hables con los representantes de la empresa de transporte ni de su seguro",
                    "Contacta a un abogado especializado en accidentes de camión ANTES de dar cualquier declaración",
                    "Preserva toda la evidencia: el camión puede tener una 'caja negra' (ECM) que registra datos críticos"
                ]
            },
            {
                "h2": "Tipos de Compensación Disponible",
                "content": "Debido a la gravedad de los accidentes de camión y los límites de seguro más altos, la compensación potencial suele ser significativamente mayor que en accidentes de auto.",
                "list": [
                    "Gastos médicos: todos los costos presentes y futuros relacionados con las lesiones",
                    "Pérdida de ingresos: salarios perdidos y pérdida de capacidad de generar ingresos futuros",
                    "Dolor y sufrimiento: compensación por el dolor físico y emocional",
                    "Daños punitivos: en casos de negligencia grave o temeraria, diseñados para castigar al responsable",
                    "Pérdida de relación conyugal: compensación para el cónyuge por la pérdida de compañía",
                    "Gastos funerarios y muerte por negligencia: si el accidente fue fatal"
                ]
            },
            {
                "h2": "¿Cuánto Tiempo Tengo para Demandar?",
                "content": "El plazo de prescripción para demandar por un accidente de camión varía por estado, pero generalmente es de 1 a 3 años desde la fecha del accidente. Sin embargo, hay particularidades importantes: si el accidente involucra a una entidad gubernamental, el plazo puede ser tan corto como 6 meses. Además, ciertos avisos deben darse dentro de días del accidente. No esperes: contacta a un abogado inmediatamente."
            }
        ],
        "faqs": [
            {
                "question": "¿Qué es la caja negra (ECM) de un camión y por qué es importante?",
                "answer": "El Módulo de Control Electrónico (ECM) es como la caja negra de un avión. Registra datos críticos como velocidad, frenado, revoluciones del motor, y actividad del conductor en los segundos previos al accidente. Esta evidencia puede ser crucial para determinar responsabilidad. Es importante que un abogado solicite una orden de preservación de evidencia inmediatamente después del accidente."
            },
            {
                "question": "¿Las regulaciones de horas de servicio afectan mi caso?",
                "answer": "Sí, son fundamentales. Los conductores de camiones están limitados a 11 horas de conducción después de 10 horas consecutivas fuera de servicio, y no pueden conducir más de 14 horas después de comenzar su turno. Si el conductor violó estas regulaciones, es evidencia de negligencia per se, lo que fortalece significativamente tu caso."
            },
            {
                "question": "¿Puedo demandar si el accidente fue en otro estado?",
                "answer": "Sí. Los abogados especializados en accidentes de camión suelen manejar casos en múltiples jurisdicciones. El caso puede presentarse en el estado donde ocurrió el accidente, donde tiene su sede la empresa de transporte, o incluso donde resides. Tu abogado determinará la mejor jurisdicción para maximizar tu compensación."
            },
            {
                "question": "¿Cuánto cuesta una consulta con un abogado especializado en accidentes de camión?",
                "answer": "La mayoría de los abogados de lesiones personales ofrecen consultas iniciales completamente gratuitas. Trabajan bajo honorarios de contingencia, lo que significa que no pagas nada a menos que ellos ganen tu caso."
            }
        ]
    },
    {
        "id": "necesito-abogado-accidente",
        "slug": "necesito-abogado-despues-accidente",
        "title": "¿Necesito un Abogado Después de un Accidente? Guía para Decidir",
        "meta_desc": "¿Necesitas un abogado tras un accidente? 5 señales de que SÍ lo necesitas y 3 situaciones donde NO. Casos reales con y sin abogado. Consulta gratis.",
        "keywords": "necesito abogado tras accidente, do I need a lawyer after a car accident, cuándo contratar abogado accidente, sin abogado vs con abogado",
        "h1": "¿Necesito un Abogado Después de un Accidente?",
        "intro": "Es una de las preguntas más comunes después de sufrir un accidente: ¿realmente necesito un abogado? La respuesta corta es: depende. Mientras que algunos casos pueden manejarse directamente con la aseguradora, otros requieren absolutamente la representación de un abogado experimentado. Esta guía te ayudará a tomar esa decisión con información clara y objetiva.",
        "sections": [
            {
                "h2": "5 Señales de que NECESITAS un Abogado",
                "content": "Estas son las banderas rojas que indican que deberías buscar representación legal antes de tomar cualquier decisión:",
                "numbered": [
                    "Sufriste lesiones que requieren tratamiento médico continuo o especializado",
                    "El accidente resultó en una discapacidad temporal o permanente",
                    "La aseguradora te está ofreciendo un acuerdo rápido por una cantidad baja",
                    "Hay disputa sobre quién causó el accidente",
                    "El accidente involucra a múltiples partes o a una entidad comercial (camión, Uber, empresa)"
                ]
            },
            {
                "h2": "3 Situaciones donde NO Necesitas un Abogado",
                "content": "Aunque siempre es recomendable consultar con un abogado, hay situaciones donde manejar el caso directamente puede tener sentido si eres cuidadoso:",
                "numbered": [
                    "El accidente fue menor (sin lesiones o lesiones muy leves que no requirieron atención médica)",
                    "La responsabilidad está clara y la aseguradora acepta responsabilidad sin disputa",
                    "Los daños son mínimos (menos de $5,000) y no hay lesiones significativas"
                ]
            },
            {
                "h2": "Casos Reales: Con Abogado vs. Sin Abogado",
                "content": "Los estudios muestran que las víctimas representadas por abogados reciben entre 2 y 3.5 veces más compensación que aquellas que manejan su caso solas. Aquí presentamos ejemplos basados en datos reales:",
                "list": [
                    "Caso 1 (Latigazo cervical): Sin abogado: $3,500 | Con abogado: $12,000",
                    "Caso 2 (Fractura de brazo): Sin abogado: $8,000 | Con abogado: $35,000",
                    "Caso 3 (Lesión de espalda): Sin abogado: $15,000 | Con abogado: $85,000",
                    "Caso 4 (Cirugía de rodilla): Sin abogado: $25,000 | Con abogado: $120,000",
                    "Caso 5 (Accidente de camión): Sin abogado: $40,000 | Con abogado: $350,000"
                ]
            },
            {
                "h2": "¿Cuánto Cuesta un Abogado? (Honorarios de Contingencia)",
                "content": "Los abogados de lesiones personales trabajan bajo un modelo de honorarios de contingencia. Esto significa que no pagas nada por adelantado. El abogado recibe un porcentaje acordado de la compensación final, pero solo si gana tu caso. Los porcentajes típicos son: 33% si el caso se resuelve antes de demandar, 35-40% si es necesario presentar una demanda, y hasta 40-45% si el caso llega a juicio o apelación.",
                "list": [
                    "Consulta inicial: 100% gratuita y sin compromiso",
                    "Sin recuperación = sin honorarios legales",
                    "Los costos administrativos se descuentan del acuerdo final"
                ]
            },
            {
                "h2": "Preguntas para Hacer Antes de Contratar un Abogado",
                "content": "Antes de firmar un contrato de representación, haz estas preguntas para asegurarte de que el abogado es adecuado para ti:",
                "numbered": [
                    "¿Cuántos años de experiencia tienes en casos como el mío?",
                    "¿Cuál es tu tasa de éxito en casos similares?",
                    "¿Quién manejará mi caso directamente? (el abogado o un asistente)",
                    "¿Cuál es tu estructura de honorarios específica para mi caso?",
                    "¿Cuánto tiempo estimas que tomará resolver mi caso?",
                    "¿Hay algún costo que deba pagar aunque perdamos el caso?",
                    "¿Prefieres llegar a un acuerdo o ir a juicio?"
                ]
            }
        ],
        "faqs": [
            {
                "question": "¿Puedo negociar con la aseguradora sin un abogado?",
                "answer": "Sí, puedes, pero no es recomendable. Las aseguradoras tienen años de experiencia negociando reclamos y saben exactamente qué tácticas usar para minimizar los pagos. Sin un abogado, estás en desventaja. Las estadísticas muestran que las personas con abogado reciben compensaciones significativamente más altas."
            },
            {
                "question": "¿Cuándo debo contactar a un abogado después del accidente?",
                "answer": "Lo antes posible. Idealmente dentro de las primeras 24-48 horas después del accidente. Cuanto antes involucres a un abogado, más rápido puede comenzar a investigar, preservar evidencia, y comunicarse con las aseguradoras en tu nombre."
            },
            {
                "question": "¿Qué pasa si no puedo pagar un abogado?",
                "answer": "No te preocupes. Como se mencionó, los abogados de lesiones personales trabajan bajo honorarios de contingencia. No necesitas dinero por adelantado. La consulta inicial es gratuita y solo pagas si ellos ganan tu caso."
            }
        ]
    },
    {
        "id": "abogado-accidentes-moto",
        "slug": "abogado-accidentes-motocicleta",
        "title": "Abogado de Accidentes de Motocicleta: Protege tus Derechos",
        "meta_desc": "Abogado especializado en accidentes de motocicleta. Lesiones comunes, compensación, sesgo antimotociclista. Consulta gratuita.",
        "keywords": "abogado accidentes motocicleta, motorcycle accident attorney, lesiones moto abogado, compensación accidente moto, sesgo motociclista",
        "h1": "Abogado Especializado en Accidentes de Motocicleta",
        "intro": "Conducir una motocicleta ofrece una sensación de libertad que ningún otro vehículo puede igualar. Sin embargo, esta libertad viene con riesgos significativos. Los motociclistas tienen 28 veces más probabilidades de morir en un accidente que los ocupantes de un automóvil. Cuando ocurre un accidente, las consecuencias suelen ser graves, y la batalla legal que sigue tiene sus propias complejidades únicas.",
        "sections": [
            {
                "h2": "Estadísticas de Accidentes de Motocicleta",
                "content": "Entender la magnitud del problema es el primer paso para apreciar por qué necesitas representación legal especializada si has estado en un accidente de moto.",
                "list": [
                    "Los motociclistas representan el 14% de todas las muertes en accidentes de tránsito, pero solo el 3% de los vehículos registrados",
                    "El 80% de los accidentes de moto resultan en lesiones o muerte (vs. 20% en autos)",
                    "Las lesiones en la cabeza son la causa principal de muerte en accidentes de moto",
                    "El uso del casco reduce el riesgo de muerte en un 37% y el de lesiones cerebrales en un 67%",
                    "La mayoría de los accidentes de moto (60%) ocurren en intersecciones"
                ]
            },
            {
                "h2": "Lesiones Comunes en Accidentes de Motocicleta",
                "content": "Las lesiones en accidentes de moto tienden a ser más graves que en accidentes de auto debido a la falta de protección del conductor. Conocer las lesiones más comunes te ayudará a entender mejor tu caso:",
                "list": [
                    "Lesiones en la cabeza y traumatismo craneoencefálico (TCE)",
                    "Lesiones en la columna vertebral y médula espinal",
                    "Fracturas de huesos largos (fémur, tibia, húmero)",
                    "Lesiones por abrasión (road rash) que pueden requerir injertos de piel",
                    "Lesiones en extremidades inferiores (pies, tobillos, rodillas)",
                    "Lesiones internas (órganos dañados, hemorragias internas)"
                ]
            },
            {
                "h2": "El Sesgo contra Motociclistas: Cómo Manejarlo",
                "content": "Desafortunadamente, existe un sesgo generalizado contra los motociclistas en el sistema legal. Los jurados y ajustadores de seguros a menudo asumen que el motociclista fue imprudente o que 'se lo buscó'. Un abogado experimentado sabe cómo contrarrestar este sesgo con evidencia y estrategia legal.",
                "numbered": [
                    "Documentación exhaustiva de la escena para probar que no fue tu culpa",
                    "Testigos independientes que confirmen la conducción responsable",
                    "Reconstrucción del accidente por peritos especializados",
                    "Evidencia de tu historial de conducción segura y entrenamiento",
                    "Argumentación legal que se anticipe a los prejuicios del jurado"
                ]
            },
            {
                "h2": "Compensación Disponible para Accidentes de Moto",
                "content": "Debido a la gravedad de las lesiones, la compensación en casos de accidentes de moto suele ser significativa. Los tipos de compensación disponibles incluyen:",
                "list": [
                    "Gastos médicos: hospitalización, cirugías, rehabilitación, medicamentos",
                    "Pérdida de ingresos: salarios perdidos y capacidad reducida de generar ingresos",
                    "Daños por dolor y sufrimiento: compensación por el trauma físico y emocional",
                    "Daños punitivos: en casos de negligencia grave o conducción temeraria",
                    "Desfiguración y discapacidad permanente: compensación adicional por cicatrices o pérdida de función"
                ]
            },
            {
                "h2": "Preguntas Frecuentes Específicas de Motociclistas",
                "content": "Las siguientes son preguntas que todo motociclista debe considerar después de un accidente:",
                "numbered": [
                    "¿El hecho de no llevar casco afecta mi caso? Depende del estado. En estados con ley de casco obligatorio, no usar casco puede reducir tu compensación. En estados sin esta ley, no debería afectar.",
                    "¿Puedo recibir compensación si no tengo licencia de moto? Sí, pero puede afectar tu caso. La falta de licencia puede ser usada en tu contra como evidencia de negligencia comparativa.",
                    "¿El seguro de mi moto cubre mis lesiones? Depende de tu póliza. El seguro de responsabilidad civil no cubre tus lesiones, pero el seguro de protección contra lesiones personales (PIP) o el seguro médico pueden hacerlo.",
                    "¿Qué pasa si el conductor que me golpeó huyó? Si el conductor es identificado, puedes presentar una reclamación como en cualquier accidente. Si no es identificado, tu seguro de motorista no asegurado (UM) puede cubrir tus lesiones."
                ]
            }
        ],
        "faqs": [
            {
                "question": "¿Por qué hay sesgo contra los motociclistas en los tribunales?",
                "answer": "Existe el estereotipo de que los motociclistas son imprudentes o temerarios. Los ajustadores de seguros y algunos jurados pueden asumir que el motociclista 'se lo buscó' o estaba haciendo acrobacias. Un abogado experto sabe cómo contrarrestar estos sesgos presentando evidencia objetiva y testimonios de expertos."
            },
            {
                "question": "¿Es más difícil ganar un caso de accidente de moto?",
                "answer": "No necesariamente más difícil, pero requiere un abogado con experiencia específica en accidentes de moto. Las estrategias legales son diferentes: necesitas peritos en reconstrucción de accidentes, conocimiento de las leyes específicas de motocicletas en tu estado, y habilidades para contrarrestar el sesgo del jurado."
            },
            {
                "question": "¿Cuánto tiempo toma resolver un caso de accidente de moto?",
                "answer": "El tiempo varía según la gravedad. Casos con lesiones claras y responsabilidad definida pueden resolverse en 6-12 meses. Casos más complejos con lesiones graves pueden tomar de 1 a 3 años, especialmente si requieren litigio."
            },
            {
                "question": "¿Debo hablar con la policía si tuve un accidente de moto?",
                "answer": "Sí, siempre debes llamar a la policía después de un accidente de moto. El informe policial es una pieza clave de evidencia. Sin embargo, limítate a dar los hechos objetivos: lugar, hora, lo que pasó. No admitas culpa ni especules sobre las causas del accidente."
            },
            {
                "question": "¿El casco evita lesiones cerebrales en un accidente de moto?",
                "answer": "El casco reduce significativamente el riesgo de lesiones cerebrales graves y fatales, pero no las elimina por completo. Un casco certificado DOT reduce el riesgo de muerte en un 37% y el de lesiones cerebrales en un 67%. Siempre usa un casco de calidad, independientemente de las leyes de tu estado."
            }
        ]
    }
]


# ─── PLANTILLA HTML ───────────────────────────────────────────────────────

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <meta name="description" content="{meta_desc}">
    <meta name="keywords" content="{keywords}">
    <meta name="robots" content="index, follow">
    <meta name="author" content="Proyecto Infinito">
    <meta name="language" content="Spanish">
    
    <!-- Open Graph -->
    <meta property="og:type" content="article">
    <meta property="og:title" content="{title}">
    <meta property="og:description" content="{meta_desc}">
    <meta property="og:locale" content="es_ES">
    <meta property="og:site_name" content="Proyecto Infinito">
    
    <!-- Twitter Card -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{title}">
    <meta name="twitter:description" content="{meta_desc}">
    
    <!-- Canonical -->
    <link rel="canonical" href="https://proyectoinfinito.com/{slug}/">
    
    <!-- FAQ Schema -->
    <script type="application/ld+json">
{faq_schema}
    </script>
    
    <!-- Article Schema -->
    <script type="application/ld+json">
{article_schema}
    </script>
    
    <style>
        *{{margin:0;padding:0;box-sizing:border-box}}
        :root{{--bg:#050508;--grn:#00ff41;--cy:#00f0ff;--text:#c8d6e5;--dim:#2d2d44;--card:#0a0a14;--border:rgba(0,255,65,0.12)}}
        body{{font-family:'Courier New',monospace;background:var(--bg);color:var(--text);line-height:1.8;padding:0}}
        .container{{max-width:900px;margin:0 auto;padding:20px}}
        header{{border-bottom:1px solid var(--border);padding:20px 0 16px;margin-bottom:24px}}
        .badge{{font-size:10px;color:var(--grn);text-transform:uppercase;letter-spacing:2px;display:flex;align-items:center;gap:6px;margin-bottom:8px}}
        .badge .dot{{width:5px;height:5px;border-radius:50%;background:var(--grn);animation:pulse 2s ease-in-out infinite}}
        @keyframes pulse{{0%,100%{{opacity:1}}50%{{opacity:0.3}}}}
        h1{{font-size:26px;color:var(--cy);margin:8px 0 12px;line-height:1.3}}
        .meta{{font-size:10px;color:var(--dim);letter-spacing:1px;margin-bottom:4px}}
        .intro{{font-size:13px;color:var(--text);line-height:1.9;margin-bottom:30px;padding:16px;border-left:2px solid var(--grn);background:rgba(0,255,65,0.02)}}
        h2{{font-size:18px;color:var(--grn);margin:28px 0 12px;padding-bottom:6px;border-bottom:1px solid var(--border);letter-spacing:1px}}
        h3{{font-size:14px;color:var(--cy);margin:18px 0 8px;letter-spacing:0.5px}}
        p{{font-size:13px;margin:10px 0;color:var(--text)}}
        ul,ol{{margin:10px 0 10px 20px}}
        li{{font-size:13px;margin:6px 0;color:var(--text)}}
        li::marker{{color:var(--grn)}}
        .cta{{margin:30px 0;padding:20px;border:1px solid var(--border);background:rgba(0,255,65,0.03);text-align:center}}
        .cta p{{font-size:12px;color:var(--dim);margin-bottom:10px}}
        .cta .btn{{display:inline-block;padding:10px 28px;border:1px solid var(--grn);color:var(--grn);text-decoration:none;font-size:11px;letter-spacing:2px;text-transform:uppercase;transition:all 0.3s}}
        .cta .btn:hover{{background:var(--grn);color:#000}}
        .faq-section{{margin:30px 0}}
        .faq-item{{padding:14px 16px;border:1px solid var(--border);margin-bottom:8px}}
        .faq-q{{font-size:12px;color:var(--cy);font-weight:600;margin-bottom:6px}}
        .faq-a{{font-size:12px;color:var(--dim);line-height:1.7}}
        footer{{margin-top:40px;padding:16px 0;border-top:1px solid var(--border);text-align:center;font-size:9px;color:var(--dim);letter-spacing:1px}}
        @media(max-width:768px){{.container{{padding:12px}}h1{{font-size:20px}}h2{{font-size:16px}}}}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <div class="badge"><span class="dot"></span> PROYECTO INFINITO · ABOGADOS DE ACCIDENTES</div>
            <div class="meta">Actualizado: {fecha} | Tiempo de lectura: {tiempo_lectura} min</div>
            <h1>{h1}</h1>
        </header>
        
        <div class="intro">{intro}</div>

{cuerpo}

        <div class="cta">
            <p>¿Has sufrido un accidente? No esperes m&aacute;s. Tu consulta inicial es completamente gratuita y sin compromiso.</p>
            <a href="#" class="btn">Solicitar Consulta Gratuita</a>
        </div>

        <div class="faq-section">
            <h2>Preguntas Frecuentes (FAQ)</h2>
{faqs_html}
        </div>

        <footer>
            <strong>PROYECTO INFINITO</strong> &mdash; Contenido SEO &middot; Nicho: Abogados de Accidentes<br>
            Generado por SEO Oracle &middot; Junio 2026 &middot; CPC Promedio: $220
        </footer>
    </div>
</body>
</html>"""


# ─── FUNCIONES DEL GENERADOR ──────────────────────────────────────────────

def build_section_html(section: Dict) -> str:
    """Convierte una sección del artículo a HTML."""
    html = f"<h2>{section['h2']}</h2>\n<p>{section['content']}</p>\n"
    
    if 'subsections' in section:
        for sub in section['subsections']:
            html += f"<h3>{sub['h3']}</h3>\n<p>{sub['content']}</p>\n"
    
    if 'list' in section:
        html += "<ul>\n"
        for item in section['list']:
            html += f"    <li>{item}</li>\n"
        html += "</ul>\n"
    
    if 'numbered' in section:
        html += "<ol>\n"
        for i, item in enumerate(section['numbered'], 1):
            html += f"    <li>{item}</li>\n"
        html += "</ol>\n"
    
    return html


def build_faq_schema(articulo: Dict) -> str:
    """Genera el JSON-LD de FAQ Schema."""
    faqs = articulo.get('faqs', [])
    if not faqs:
        return ""
    
    items = []
    for faq in faqs:
        items.append(f'        {{"@type":"Question","name":{json.dumps(faq["question"], ensure_ascii=False)},"acceptedAnswer":{{"@type":"Answer","text":{json.dumps(faq["answer"], ensure_ascii=False)}}}}}')
    
    schema = '{\n'
    schema += '    "@context": "https://schema.org",\n'
    schema += '    "@type": "FAQPage",\n'
    schema += '    "mainEntity": [\n'
    schema += ',\n'.join(items)
    schema += '\n    ]\n'
    schema += '}'
    return schema


def build_article_schema(articulo: Dict) -> str:
    """Genera el JSON-LD de Article Schema."""
    schema = '{\n'
    schema += '    "@context": "https://schema.org",\n'
    schema += '    "@type": "Article",\n'
    schema += f'    "headline": {json.dumps(articulo["title"], ensure_ascii=False)},\n'
    schema += f'    "description": {json.dumps(articulo["meta_desc"], ensure_ascii=False)},\n'
    schema += f'    "datePublished": "2026-06-20",\n'
    schema += f'    "dateModified": "{datetime.now().strftime("%Y-%m-%d")}",\n'
    schema += '    "author": {\n'
    schema += '        "@type": "Person",\n'
    schema += '        "name": "Romny (El Joker) — Proyecto Infinito"\n'
    schema += '    },\n'
    schema += '    "publisher": {\n'
    schema += '        "@type": "Organization",\n'
    schema += '        "name": "Proyecto Infinito"\n'
    schema += '    }\n'
    schema += '}'
    return schema


def build_faqs_html(articulo: Dict) -> str:
    """Genera el HTML de las preguntas frecuentes."""
    faqs = articulo.get('faqs', [])
    if not faqs:
        return "<p>No hay preguntas frecuentes disponibles.</p>"
    
    html = ""
    for faq in faqs:
        html += '        <div class="faq-item">\n'
        html += f'            <div class="faq-q">{faq["question"]}</div>\n'
        html += f'            <div class="faq-a">{faq["answer"]}</div>\n'
        html += '        </div>\n'
    
    return html


def build_cuerpo_html(articulo: Dict) -> str:
    """Construye el cuerpo completo del artículo."""
    parts = []
    for section in articulo['sections']:
        parts.append(build_section_html(section))
    
    # Add disclaimer
    parts.append(
        '<div style="margin:30px 0;padding:12px;border:1px solid rgba(239,68,68,0.2);background:rgba(239,68,68,0.03);font-size:11px;color:var(--dim)">'
        '<strong style="color:var(--rd)">⚠️ Aviso Legal:</strong> Este contenido es informativo y no constituye asesoramiento legal. '
        'Cada caso es único y debe ser evaluado por un abogado calificado. Los resultados pasados no garantizan resultados futuros.</div>'
    )
    
    return "\n".join(parts)


def generate_article(articulo: Dict, output_dir: str) -> str:
    """Genera un archivo HTML completo para un artículo."""
    # Calcular tiempo de lectura
    palabras_totales = len(articulo['intro'].split())
    for section in articulo['sections']:
        palabras_totales += len(section.get('content', '').split())
        if 'list' in section:
            for item in section['list']:
                palabras_totales += len(item.split())
        if 'numbered' in section:
            for item in section['numbered']:
                palabras_totales += len(item.split())
        if 'subsections' in section:
            for sub in section['subsections']:
                palabras_totales += len(sub.get('content', '').split())
    
    tiempo_lectura = max(5, round(palabras_totales / 200))
    
    # Generar schemas y HTML
    faq_schema = build_faq_schema(articulo)
    article_schema = build_article_schema(articulo)
    faqs_html = build_faqs_html(articulo)
    cuerpo = build_cuerpo_html(articulo)
    
    # Llenar template
    html = HTML_TEMPLATE.format(
        title=articulo['title'],
        meta_desc=articulo['meta_desc'],
        keywords=articulo['keywords'],
        slug=articulo['slug'],
        faq_schema=faq_schema,
        article_schema=article_schema,
        fecha=datetime.now().strftime("%d/%m/%Y"),
        tiempo_lectura=tiempo_lectura,
        h1=articulo['h1'],
        intro=articulo['intro'],
        cuerpo=cuerpo,
        faqs_html=faqs_html
    )
    
    # Guardar archivo
    os.makedirs(output_dir, exist_ok=True)
    filename = f"{articulo['slug']}.html"
    filepath = os.path.join(output_dir, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)
    
    return filepath


# ─── MAIN ────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Generador Automático de Contenido SEO — Proyecto Infinito",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python generar_contenido.py              # Genera 5 artículos principales
  python generar_contenido.py --all        # Genera TODOS los artículos del nicho
  python generar_contenido.py --output ./salida   # Directorio personalizado
  python generar_contenido.py --list       # Lista los artículos disponibles
        """
    )
    parser.add_argument('--all', action='store_true', help='Generar todos los artículos (no solo los 5 principales)')
    parser.add_argument('--output', type=str, default='contenido', help='Directorio de salida (default: ./contenido)')
    parser.add_argument('--list', action='store_true', help='Listar artículos disponibles')
    parser.add_argument('--slug', type=str, help='Generar solo un artículo específico por slug')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("  📄 GENERADOR DE CONTENIDO SEO — Proyecto Infinito")
    print("  Nicho: Abogados de Accidentes (CPC $150-$300)")
    print("=" * 60)
    
    if args.list:
        print(f"\n  Artículos disponibles ({len(ARTICULOS)}):")
        print("-" * 50)
        for i, art in enumerate(ARTICULOS, 1):
            faq_count = len(art.get('faqs', []))
            sections_count = len(art.get('sections', []))
            print(f"  {i:2d}. {art['title']}")
            print(f"      Slug: {art['slug']}")
            print(f"      Secciones: {sections_count} | FAQs: {faq_count}")
            print()
        print("=" * 60)
        return
    
    # Determinar qué artículos generar
    if args.slug:
        articulos = [a for a in ARTICULOS if a['slug'] == args.slug]
        if not articulos:
            print(f"\n  ❌ No se encontró el artículo con slug: {args.slug}")
            return
    elif args.all:
        articulos = ARTICULOS
    else:
        articulos = ARTICULOS[:5]  # Primeros 5 por defecto
    
    output_dir = os.path.abspath(args.output)
    
    print(f"\n  📂 Generando en: {output_dir}")
    print(f"  📝 Artículos: {len(articulos)}")
    print("-" * 50)
    
    generated = []
    for art in articulos:
        filepath = generate_article(art, output_dir)
        faq_count = len(art.get('faqs', []))
        words = sum(len(s.get('content', '').split()) for s in art.get('sections', []))
        print(f"  ✅ {art['slug']}.html")
        print(f"     {art['title'][:55]}...")
        print(f"     {words} palabras · {faq_count} FAQs")
        generated.append(filepath)
        print()
    
    # Resumen
    print("-" * 50)
    print(f"  ✅ {len(generated)} archivos generados exitosamente")
    print(f"  📁 Directorio: {output_dir}")
    
    # Tamaño total
    total_bytes = sum(os.path.getsize(f) for f in generated if os.path.exists(f))
    print(f"  💾 Peso total: {total_bytes:,} bytes")
    print()
    print("  📋 Archivos generados:")
    for f in generated:
        slug = os.path.basename(f).replace('.html', '')
        art = next((a for a in ARTICULOS if a['slug'] == slug), None)
        if art:
            # Contar FAQs con Schema
            schema_faqs = sum(1 for _ in art.get('faqs', []))
            print(f"     └─ {os.path.basename(f)} ({schema_faqs} FAQ Schema)")
    
    print()
    print("  💡 Para generar más artículos:")
    print("     python generar_contenido.py --all")
    print("     python generar_contenido.py --slug <slug>")
    print()
    print("=" * 60)


if __name__ == "__main__":
    main()
