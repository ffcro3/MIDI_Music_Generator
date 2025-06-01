# music_generator.py

import random
import mido

class MusicGenerator:
    def __init__(self):
        self.scales = {
            'Major': {
                'intervals': [0, 2, 4, 5, 7, 9, 11],
                'chords': {
                    'I': [0, 4, 7],
                    'ii': [2, 5, 9],
                    'iii': [4, 7, 11],
                    'IV': [5, 9, 12],
                    'V': [7, 11, 14],
                    'vi': [9, 12, 16],
                    'vii°': [11, 14, 17]
                }
            },
            'Minor': { # Natural Minor
                'intervals': [0, 2, 3, 5, 7, 8, 10],
                'chords': {
                    'i': [0, 3, 7],
                    'ii°': [2, 5, 8],
                    'III': [3, 7, 10],
                    'iv': [5, 8, 12],
                    'V': [7, 10, 14], # Pode ser V maior/dominante para cadência
                    'v': [7, 10, 14], # V menor
                    'VI': [8, 12, 15],
                    'VII': [10, 14, 17]
                }
            }
        }
        self.root_notes = {
            'C': 60, 'C#': 61, 'D': 62, 'D#': 63, 'E': 64, 'F': 65,
            'F#': 66, 'G': 67, 'G#': 68, 'A': 69, 'A#': 70, 'B': 71
        }
        self.ticks_per_beat = 480

        # --- Dicionário de Características do Liquid Funk (Detalhado) ---
        self.liquid_funk_caracteristicas = {
            "genero": "Liquid Funk",
            "bpm_faixa": (160, 175),
            "bpm_medio_sugerido": 168,
            "atmosfera_geral": "Suave, Melódico, Soulful, Atmosférico, Emocional, Otimista/Nostálgico",
            "influencias_primarias": ["Jazz", "Funk", "Soul", "R&B", "Música Clássica (em arranjos/melodias)"],
            "artistas_referencia": ["London Elektricity", "Hybrid Minds", "Keeno", "Camo & Krooked", "Catching Cairo (vocais)"],

            "bassline": {
                "nome": "Bassline 'Rolling'",
                "descricao": "Linha de baixo contínua, melódica e suave, servindo como base harmônica e rítmica, frequentemente com um 'bounce' sutil e envolvente.",
                "caracteristicas_ritmicas": {
                    "fluxo_predominante": "Contínuo e Fluido ('Rolling')",
                    "sincopacao": "Sutil e Orgânica (notas fora do tempo forte que se encaixam naturalmente no groove, sem quebras abruptas. Pense na fluidez de um baixista de jazz/funk.)",
                    "duracao_notas_comuns": ["Colcheias", "Semínimas"], # Com uso forte de legato e sustain
                    "uso_pausas_estrategicas": "Mínimo a Moderado (pausas curtas para respiro melódico ou para realçar um ataque, mas sem quebrar o fluxo.)",
                    "variacao_ritmica": "Orgânica e Gradual (variações sutis para manter o interesse, como mudança de notas por compasso ou pequenas figuras rítmicas sincopadas que complementam a bateria.)",
                },
                "caracteristicas_melodicas_harmonicas": {
                    "papel_melodico": "Crucial (linha melódica própria que não só fundamenta a harmonia, mas também adiciona profundidade e emoção. Pense no baixo como uma segunda voz.)",
                    "notas_comuns_relativas_acorde": [
                        "Tônica (fundamental do acorde)",
                        "Quinta (reforça a tônica, estabilidade)",
                        "Terça (maior ou menor, define a qualidade do acorde)",
                        "Sexta/Sétima (adiciona cor jazzística/soulful, cria tensão e resolução sutil. Essencial para a sonoridade Liquid.)",
                        "Nona/Décima Primeira/Décima Terceira (extensões que enriquecem ainda mais a harmonia, muito comum em acordes de jazz.)",
                        "Notas de Passagem Cromáticas ou Diatônicas (para conectar frases melódicas de forma suave e expressiva.)"
                    ],
                    "escalas_comuns": [
                        "Escala Maior", "Escala Menor Natural", "Escala Menor Harmônica",
                        "Escala Menor Melódica Ascendente", "Modo Dórico", "Modo Lídio", "Modo Mixolídio"
                    ],
                    "faixa_frequencia_foco": "Sub-grave (limpo, profundo e presente) e Médio-grave (quente, suave e musical, com presença para as notas melódicas se destacarem).",
                    "complexidade_harmonica": "Moderada a Alta (frequentemente segue ou implica progressões de acordes ricas e com inversões, com notas de baixo que sugerem acordes estendidos.)",
                },
                "caracteristicas_de_performance_midi": {
                    "velocity": {
                        "tipo": "Variada e Sutil",
                        "detalhe": "Notas com diferentes intensidades para expressividade e toque 'humano'. Ataques mais fortes no início de frases melódicas ou pontos de ênfase; notas de passagem e sustain mais suaves. Simula a nuance de um baixista tocando.",
                    },
                    "legato_glide": {
                        "legato_uso": "Extenso (essencial para o fluxo 'rolling', notas se sobrepondo ligeiramente para evitar espaços e manter a continuidade.)",
                        "glide_uso": "Comum (portamento suave e melódico entre notas, usado intencionalmente para criar deslizes expressivos e conexões fluidas.)",
                    },
                    "duracao_notas_midi": "Maior duração (gate alto) para a maioria das notas, criando conexão e sustain. Notas mais curtas podem ser usadas para ghost notes ou para dar um 'punch' específico.",
                    "ghost_notes": "Comum (pequenas notas de baixa velocity/duração inseridas entre as notas principais para adicionar groove e um toque 'funky' sutil, sem atrapalhar o fluxo principal.)"
                },
                "common_root_notes": {
                    "descricao": "As notas tônicas/fundamentais mais frequentemente usadas, valorizando a ressonância em sub-graves e a versatilidade harmônica.",
                    "notas": ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
                },
                "common_patterns_midi": {
                    "padrao_1_simples_rolling": {
                        "descricao": "Padrão fundamental de colcheias ou semínimas contínuas, focando na tônica e quinta do acorde, com forte uso de legato, criando uma base sólida e envolvente.",
                        "exemplo_midi_relativo": [
                            {"note": 0, "duration": "8n", "velocity_range": (80, 95)},
                            {"note": 0, "duration": "8n", "velocity_range": (80, 95)},
                            {"note": 7, "duration": "8n", "velocity_range": (80, 95)},
                            {"note": 0, "duration": "8n", "velocity_range": (80, 95)},
                        ]
                    },
                    "padrao_2_melodico_jazzy": {
                        "descricao": "Linha mais melódica, explorando terças, sextas, sétimas e até extensões como nonas, com saltos e notas de passagem que criam frases mais complexas e sofisticadas.",
                        "exemplo_midi_relativo": [
                            {"note": 0, "duration": "4n", "velocity_range": (90, 100)},
                            {"note": 3, "duration": "8n", "velocity_range": (70, 85)},
                            {"note": 5, "duration": "8n", "velocity_range": (70, 85)},
                            {"note": 7, "duration": "4n", "velocity_range": (85, 95)},
                            {"note": 10, "duration": "8n", "velocity_range": (75, 90), "glide_to": 12},
                            {"note": 12, "duration": "8n", "velocity_range": (75, 90)},
                            {"note": 14, "duration": "8n", "velocity_range": (65, 80)},
                        ]
                    },
                    "padrao_3_syncopado_funk": {
                        "descricao": "Padrão com mais sincopação e uso de ghost notes, emulando um groove de baixista de funk/R&B, mas ainda mantendo o fluxo 'rolling'.",
                        "exemplo_midi_relativo": [
                            {"note": 0, "duration": "8n", "velocity_range": (90, 100)},
                            {"note": 7, "duration": "16n", "velocity_range": (60, 75), "ghost_note": True},
                            {"note": 0, "duration": "8n", "velocity_range": (80, 90)},
                            {"note": 5, "duration": "8n", "velocity_range": (70, 85)},
                            {"note": 7, "duration": "8n", "velocity_range": (85, 95)},
                            {"note": 0, "duration": "8n.", "velocity_range": (90, 100)},
                            {"note": 10, "duration": "16n", "velocity_range": (65, 80)},
                        ]
                    },
                     "padrao_4_arpeggiated_or_broken_chord": {
                        "descricao": "Linha de baixo que explora as notas do acorde de forma arpejada ou como um 'broken chord', adicionando movimento harmônico e melódico.",
                        "exemplo_midi_relativo": [
                            {"note": 0, "duration": "8n", "velocity_range": (85, 95)},
                            {"note": 4, "duration": "8n", "velocity_range": (80, 90)},
                            {"note": 7, "duration": "8n", "velocity_range": (80, 90)},
                            {"note": 12, "duration": "8n", "velocity_range": (85, 95)},
                            {"note": 7, "duration": "8n", "velocity_range": (80, 90)},
                            {"note": 4, "duration": "8n", "velocity_range": (80, 90)},
                        ]
                    }
                }
            }
        }
        # Fim do dicionário Liquid Funk

        self.music_styles_data = {
            'Trance': {
                'bpm_range': (135, 145),
                'bass_rhythm_options': [self.ticks_per_beat, self.ticks_per_beat // 2, int(self.ticks_per_beat * 1.5)],
                'bass_octave_offset': -2,
                'lead_octave_offset': 0,
                'pad_octave_offset': -1,
                'arpeggio_octave_offset': 0,
                'chord_voicing_options': ['pads'],
                'chord_duration_beats': 4
            },
            'Techno': {
                'bpm_range': (120, 140),
                'bass_rhythm_options': [self.ticks_per_beat, self.ticks_per_beat // 2],
                'bass_octave_offset': -2,
                'lead_octave_offset': 0,
                'pad_octave_offset': -1,
                'arpeggio_octave_offset': 0,
                'chord_voicing_options': ['stab', 'sustained'],
                'chord_duration_beats': 1
            },
            'House': {
                'bpm_range': (115, 130),
                'bass_rhythm_options': [self.ticks_per_beat, self.ticks_per_beat // 2],
                'bass_octave_offset': -2,
                'lead_octave_offset': 0,
                'pad_octave_offset': -1,
                'arpeggio_octave_offset': 0,
                'chord_voicing_options': ['chords'],
                'chord_duration_beats': 1
            },
            'Hip-Hop': {
                'bpm_range': (80, 100),
                'bass_rhythm_options': [int(self.ticks_per_beat * 1.5), self.ticks_per_beat * 2, self.ticks_per_beat],
                'bass_octave_offset': -2,
                'lead_octave_offset': -1,
                'pad_octave_offset': -1,
                'arpeggio_octave_offset': 0,
                'chord_voicing_options': ['chords'],
                'chord_duration_beats': 2
            },
            'Trap': {
                'bpm_range': (130, 170),
                'bass_rhythm_options': [self.ticks_per_beat // 2, self.ticks_per_beat // 4],
                'bass_octave_offset': -2,
                'lead_octave_offset': 0,
                'pad_octave_offset': -1,
                'arpeggio_octave_offset': 0,
                'chord_voicing_options': ['chords'],
                'chord_duration_beats': 2
            },
            'Lofi Hip-Hop': {
                'bpm_range': (70, 90),
                'bass_rhythm_options': [int(self.ticks_per_beat * 1.5), self.ticks_per_beat * 2],
                'bass_octave_offset': -2,
                'lead_octave_offset': -1,
                'pad_octave_offset': -1,
                'arpeggio_octave_offset': 0,
                'chord_voicing_options': ['chords'],
                'chord_duration_beats': 4
            },
            'Pop': {
                'bpm_range': (100, 130),
                'bass_rhythm_options': [self.ticks_per_beat, self.ticks_per_beat // 2],
                'bass_octave_offset': -2,
                'lead_octave_offset': 0,
                'pad_octave_offset': -1,
                'arpeggio_octave_offset': 0,
                'chord_voicing_options': ['chords'],
                'chord_duration_beats': 2
            },
            'Rock': {
                'bpm_range': (90, 150),
                'bass_rhythm_options': [self.ticks_per_beat, self.ticks_per_beat // 2],
                'bass_octave_offset': -2,
                'lead_octave_offset': 0,
                'pad_octave_offset': -1,
                'arpeggio_octave_offset': 0,
                'chord_voicing_options': ['chords'],
                'chord_duration_beats': 2
            },
            # Estilo 'Drum and Bass' existente, que será aprimorado ou usado como base para Liquid Funk
            'Drum and Bass': { # Base para Drum and Bass (incluindo Liquid, mas com opção de ser mais genérico)
                'bpm_range': (160, 180),
                'bass_rhythm_options': [ # Mais opções para DnB geral, incluindo mais percussivo
                    self.ticks_per_beat,         # 1/4 (semínima)
                    self.ticks_per_beat // 2,    # 1/8 (colcheia)
                    self.ticks_per_beat // 4,    # 1/16 (semicolcheia) - para baixos mais rápidos
                    int(self.ticks_per_beat * 0.75), # dotted 1/8
                    int(self.ticks_per_beat * 1.5), # dotted 1/4
                    self.ticks_per_beat * 2      # 1/2 (mínima)
                ],
                'bass_octave_offset': -2,
                'lead_octave_offset': 0,
                'pad_octave_offset': -1,
                'arpeggio_octave_offset': 0,
                'chord_voicing_options': ['pads', 'extended', 'stab'], # Pads para Liquid, stabs para Jump Up
                'chord_duration_beats': 4 # Pode variar para stabs vs pads
            },
            'Liquid Funk': self.liquid_funk_caracteristicas # Referencia o dicionário detalhado
            , # Certifique-se de ter uma vírgula aqui se houver mais itens
            'R&B': {
                'bpm_range': (60, 90),
                'bass_rhythm_options': [int(self.ticks_per_beat * 1.5), self.ticks_per_beat * 2, self.ticks_per_beat],
                'bass_octave_offset': -2,
                'lead_octave_offset': 0,
                'pad_octave_offset': -1,
                'arpeggio_octave_offset': 0,
                'chord_voicing_options': ['chords'],
                'chord_duration_beats': 2
            },
            'Reggae': {
                'bpm_range': (60, 100),
                'bass_rhythm_options': [self.ticks_per_beat * 2, int(self.ticks_per_beat * 1.5)],
                'bass_octave_offset': -2,
                'lead_octave_offset': 0,
                'pad_octave_offset': -1,
                'arpeggio_octave_offset': 0,
                'chord_voicing_options': ['skank'],
                'chord_duration_beats': 1
            },
            'Soul': {
                'bpm_range': (70, 110),
                'bass_rhythm_options': [self.ticks_per_beat, int(self.ticks_per_beat * 0.75), self.ticks_per_beat // 2],
                'bass_octave_offset': -2,
                'lead_octave_offset': 0,
                'pad_octave_offset': -1,
                'arpeggio_octave_offset': 0,
                'chord_voicing_options': ['chords'],
                'chord_duration_beats': 2
            },
            'Dubstep': {
                'bpm_range': (135, 145),
                'bass_rhythm_options': [self.ticks_per_beat * 2, self.ticks_per_beat],
                'bass_octave_offset': -2,
                'lead_octave_offset': 0,
                'pad_octave_offset': -1,
                'arpeggio_octave_offset': 0,
                'chord_voicing_options': ['pads', 'heavy'],
                'chord_duration_beats': 4
            }
        }


    def _get_scale_notes(self, root_note_midi, scale_type, octave_offset=0):
        intervals = self.scales[scale_type]['intervals']
        return [root_note_midi + interval + (octave_offset * 12) for interval in intervals]

    def _get_chord_midi_notes(self, root_note_midi, scale_type, chord_symbol, octave_offset=0):
        if scale_type not in self.scales:
            raise ValueError(f"Tipo de escala '{scale_type}' não suportado.")
        if chord_symbol not in self.scales[scale_type]['chords']:
            raise ValueError(f"Símbolo de acorde '{chord_symbol}' não encontrado para a escala '{scale_type}'.")

        chord_intervals = self.scales[scale_type]['chords'][chord_symbol]
        chord_midi_notes = [root_note_midi + interval + (octave_offset * 12) for interval in chord_intervals]
        return chord_midi_notes

    def generate_music_parts(self, root_key_str, scale_type, bpm, num_beats,
                             generate_bass=True, generate_chords=True, generate_lead=True,
                             generate_pads=False, generate_arpeggio=False,
                             generate_drums=False,
                             music_style="Trance"):

        log_text = ""
        log_text += f"Gerando música no estilo: {music_style}\n"

        root_note_midi = self.root_notes[root_key_str]

        ticks_per_beat = self.ticks_per_beat
        us_per_beat = mido.bpm2tempo(bpm)
        total_ticks = mido.second2tick((num_beats / bpm) * 60, ticks_per_beat, us_per_beat)

        all_midi_events = {
            'bass': [],
            'chords': [],
            'lead': [],
            'pads': [],
            'arpeggio': [],
            'drums': []
        }

        style_data = self.music_styles_data.get(music_style, self.music_styles_data['Trance'])

        progression_chords = []
        if music_style == 'Trance':
            if scale_type == 'Major':
                progression_chords = ['I', 'IV', 'V', 'I']
            else:
                progression_chords = ['i', 'VI', 'VII', 'i']
                if 'V' in self.scales[scale_type]['chords']:
                    if 'VII' in progression_chords and 'V' in self.scales[scale_type]['chords']:
                        progression_chords = ['i', 'VI', 'V', 'i']
                    elif 'v' in progression_chords and 'V' in self.scales[scale_type]['chords']:
                        progression_chords = [c if c != 'v' else 'V' for c in progression_chords]
        elif music_style == 'Techno':
            progression_chords = ['i', 'iv']
        elif music_style == 'House':
            progression_chords = ['I', 'vi', 'ii', 'V'] if scale_type == 'Major' else ['i', 'VI', 'VII', 'i']
        elif music_style == 'Hip-Hop':
            progression_chords = ['i', 'iv', 'v', 'i']
        elif music_style == 'Drum and Bass' or music_style == 'Liquid Funk': # Aplica lógica similar para ambos DnB e Liquid
            if scale_type == 'Major':
                progression_chords = random.choice([
                    ['I', 'IV', 'V', 'I'],
                    ['I', 'vi', 'IV', 'V'],
                    ['I', 'ii', 'V', 'I']
                ])
            else: # Minor is more common in DnB/Liquid
                progression_chords = random.choice([
                    ['i', 'VII', 'VI', 'V'], # Classic DnB minor progression
                    ['i', 'iv', 'VII', 'III'], # Soulful minor progression
                    ['i', 'i', 'i', 'i'], # Vamping on the tonic
                    ['i', 'iv', 'v', 'i'], # Basic minor
                    ['i', 'VI', 'VII', 'i'] # Outra comum
                ])
        else:
            if scale_type == 'Major':
                progression_chords = ['I', 'IV', 'V', 'I']
            else:
                progression_chords = ['i', 'iv', 'v', 'i']

        if not progression_chords:
            log_text += "Aviso: Nenhuma progressão de acordes específica para o estilo. Usando padrão.\n"
            if scale_type == 'Major':
                progression_chords = ['I', 'IV', 'V', 'I']
            else:
                progression_chords = ['i', 'iv', 'v', 'i']

        num_chord_cycles = (num_beats // 4) // len(progression_chords) + 1

        if generate_bass:
            self._generate_bassline(all_midi_events['bass'], total_ticks, ticks_per_beat, log_text,
                                    root_note_midi, scale_type, progression_chords, style_data, music_style)

        if generate_chords or generate_pads:
            self._generate_chords_and_pads(all_midi_events['chords'], total_ticks, ticks_per_beat, log_text,
                                           root_note_midi, scale_type, progression_chords, style_data,
                                           generate_pads, music_style)

        if generate_lead:
            self._generate_lead_melody(all_midi_events['lead'], total_ticks, ticks_per_beat, log_text,
                                       root_note_midi, scale_type, progression_chords, style_data, music_style)

        if generate_arpeggio:
            self._generate_arpeggio(all_midi_events['arpeggio'], total_ticks, ticks_per_beat, log_text,
                                    root_note_midi, scale_type, progression_chords, style_data, music_style)

        if generate_drums:
            self._generate_drums(all_midi_events['drums'], total_ticks, ticks_per_beat, log_text, music_style)

        return all_midi_events, log_text, total_ticks, us_per_beat

    def _generate_bassline(self, bass_events, total_ticks, ticks_per_beat, log_text,
                           root_note_midi, scale_type, progression_chords, style_data, music_style):
        bassline_ticks_elapsed = 0
        log_text_local = "\n--- Bassline ---\n"
        bass_octave = style_data.get('bass_octave_offset', -2)
        # Use o dicionário de Liquid Funk para as escalas preferidas, se aplicável
        if music_style == 'Liquid Funk':
            # Escolha uma escala do Liquid Funk para a geração.
            # Aqui, para simplificar, vamos usar a que foi passada, mas no futuro poderíamos ter um random.choice
            # dentro das escalas comuns do Liquid Funk.
            full_scale_notes_bass_octave = self._get_scale_notes(root_note_midi, scale_type, octave_offset=bass_octave)
        else:
            full_scale_notes_bass_octave = self._get_scale_notes(root_note_midi, scale_type, octave_offset=bass_octave)

        num_chord_cycles = (total_ticks // (ticks_per_beat * 4)) + 1 # Assumindo 4 beats por acorde na progressão

        # Padrões MIDI para Liquid Funk, mapeados para ticks_per_beat
        # Adaptação das durações para ticks
        dur_map = {
            "4n": self.ticks_per_beat, # Semínima
            "8n": self.ticks_per_beat // 2, # Colcheia
            "8n.": int(self.ticks_per_beat * 0.75), # Colcheia pontuada
            "16n": self.ticks_per_beat // 4, # Semicolcheia
            "16n.": int(self.ticks_per_beat * 0.375), # Semicolcheia pontuada
            "32n": self.ticks_per_beat // 8, # Fusa
            "2n": self.ticks_per_beat * 2, # Mínima
            "1n": self.ticks_per_beat * 4 # Semibreve
        }


        for cycle_idx in range(num_chord_cycles):
            for chord_symbol in progression_chords:
                if bassline_ticks_elapsed >= total_ticks: break

                current_chord_notes_bass = self._get_chord_midi_notes(root_note_midi, scale_type, chord_symbol, octave_offset=bass_octave)
                if not current_chord_notes_bass:
                    bassline_ticks_elapsed += ticks_per_beat * 4
                    continue

                duration_chord_block_ticks = ticks_per_beat * 4
                current_block_ticks = 0

                if music_style == 'Liquid Funk':
                    # Escolha um padrão de bassline do dicionário Liquid Funk
                    chosen_pattern_name = random.choice(list(self.liquid_funk_caracteristicas['bassline']['common_patterns_midi'].keys()))
                    chosen_pattern = self.liquid_funk_caracteristicas['bassline']['common_patterns_midi'][chosen_pattern_name]['exemplo_midi_relativo']

                    # Adiciona notas ao padrão para cobrir a duração do bloco de acorde
                    pattern_idx = 0
                    while current_block_ticks < duration_chord_block_ticks:
                        if pattern_idx >= len(chosen_pattern):
                            pattern_idx = 0 # Loop back to the start of the pattern if needed

                        note_info = chosen_pattern[pattern_idx]
                        relative_note = note_info['note']
                        duration_str = note_info['duration']
                        velocity_range = note_info['velocity_range']
                        is_ghost_note = note_info.get('ghost_note', False)
                        glide_to_relative = note_info.get('glide_to', None)

                        note_duration_ticks = dur_map.get(duration_str, ticks_per_beat // 2) # Default to 1/8 if not found

                        current_note = root_note_midi + relative_note + (bass_octave * 12)
                        
                        # Apply velocity range
                        velocity = random.randint(velocity_range[0], velocity_range[1])
                        if is_ghost_note:
                            velocity = random.randint(velocity_range[0], velocity_range[0] + 15) # Smaller range for ghost
                            note_duration_ticks = min(note_duration_ticks, ticks_per_beat // 8) # Ghost notes are short

                        # Ensure note is within a reasonable bass range (e.g., C0 to C3 for MIDI 36-72)
                        current_note = max(current_note, 36) # C2
                        current_note = min(current_note, 72) # C4

                        # Add note on
                        bass_events.append(('note_on', current_note, velocity, int(bassline_ticks_elapsed)))

                        # Handle glide (simplified for now, actual pitch bend requires more)
                        if glide_to_relative is not None:
                            # For a true glide, you'd send pitch bend messages.
                            # For simplicity here, we simulate legato by extending the note duration.
                            note_off_factor = 0.99 # Very high legato for glide
                            bass_events.append(('note_off', current_note, velocity, int(bassline_ticks_elapsed + int(note_duration_ticks * note_off_factor))))
                        else:
                            # Apply legato/sustain factor
                            note_off_factor = random.uniform(0.85, 0.98) # More legato for Liquid Funk
                            bass_events.append(('note_off', current_note, velocity, int(bassline_ticks_elapsed + int(note_duration_ticks * note_off_factor))))

                        log_text_local += f"BASS (LF): Note {current_note} (MIDI) at {int(bassline_ticks_elapsed)} for {int(note_duration_ticks * note_off_factor)} ticks\n"
                        bassline_ticks_elapsed += note_duration_ticks
                        current_block_ticks += note_duration_ticks
                        pattern_idx += 1
                        if bassline_ticks_elapsed >= total_ticks: break

                else: # Lógica de bassline existente para outros estilos
                    rhythm_options = list(style_data['bass_rhythm_options'])
                    if music_style == 'Drum and Bass':
                        rhythm_options = [
                            self.ticks_per_beat,
                            self.ticks_per_beat // 2,
                            int(self.ticks_per_beat * 0.75),
                            int(self.ticks_per_beat * 1.5),
                            self.ticks_per_beat * 2
                        ]
                        if random.random() < 0.3:
                            rhythm_options.append(self.ticks_per_beat // 4)

                    note_duration_ticks = random.choice(rhythm_options)
                    min_duration = ticks_per_beat // 8
                    note_duration_ticks = max(note_duration_ticks, min_duration)

                    current_note = random.choice(current_chord_notes_bass) if random.random() < 0.7 else random.choice(full_scale_notes_bass_octave)
                    current_note = max(current_note, root_note_midi + (bass_octave * 12))
                    current_note = min(current_note, root_note_midi + (bass_octave * 12) + 24)

                    velocity = random.randint(90, 110)
                    note_off_factor = random.uniform(0.85, 0.98)

                    if bassline_ticks_elapsed + note_duration_ticks <= total_ticks:
                        bass_events.append(('note_on', current_note, velocity, int(bassline_ticks_elapsed)))
                        bass_events.append(('note_off', current_note, velocity, int(bassline_ticks_elapsed + int(note_duration_ticks * note_off_factor))))
                        log_text_local += f"BASS: Note {current_note} (MIDI) at {int(bassline_ticks_elapsed)} for {int(note_duration_ticks * note_off_factor)} ticks\n"
                        bassline_ticks_elapsed += note_duration_ticks
                        current_block_ticks += note_duration_ticks
                    else:
                        break
        log_text += log_text_local

    def _generate_chords_and_pads(self, chord_events, total_ticks, ticks_per_beat, log_text,
                                  root_note_midi, scale_type, progression_chords, style_data,
                                  generate_pads, music_style):
        chords_ticks_elapsed = 0
        log_text_local = "\n--- Chords/Pads ---\n"
        chord_octave = style_data.get('pad_octave_offset', -1)
        chord_duration_beats = style_data.get('chord_duration_beats', 4)

        num_chord_cycles = (total_ticks // (ticks_per_beat * 4)) + 1

        for cycle_idx in range(num_chord_cycles):
            for chord_symbol in progression_chords:
                if chords_ticks_elapsed >= total_ticks: break

                chord_notes = self._get_chord_midi_notes(root_note_midi, scale_type, chord_symbol, octave_offset=chord_octave)

                if music_style == 'Liquid Funk' or generate_pads: # Liquid Funk prioritiza pads e acordes estendidos
                    chord_duration_ticks = ticks_per_beat * chord_duration_beats # Pads são longos
                    velocity = random.randint(70, 95)
                    note_off_factor = 0.99 # Quase 100% de sustain
                else:
                    chord_duration_ticks = int(ticks_per_beat * random.choice([1, 2, 4]))
                    velocity = random.randint(80, 100)
                    note_off_factor = random.uniform(0.8, 0.95)

                # Lógica para acordes estendidos (aprimorada para Liquid Funk)
                if music_style == 'Liquid Funk' or 'extended' in style_data['chord_voicing_options']:
                    if chord_notes:
                        # Adiciona sétimas, nonas, etc. com base na escala
                        temp_chord_notes = list(chord_notes) # Copia para não modificar o original diretamente
                        if scale_type == 'Major':
                            # Possíveis extensões: 7M, 9, 11#, 13
                            if random.random() < 0.6: # 60% chance de adicionar 7M
                                if (temp_chord_notes[-1] + 11) <= 100: temp_chord_notes.append(temp_chord_notes[-1] + 11)
                            if random.random() < 0.3: # 30% chance de adicionar 9
                                if (temp_chord_notes[-1] + 14) <= 100: temp_chord_notes.append(temp_chord_notes[-1] + 14)
                        elif scale_type == 'Minor':
                            # Possíveis extensões: b7, 9, 11, b13
                            if random.random() < 0.7: # 70% chance de adicionar b7
                                if (temp_chord_notes[-1] + 10) <= 100: temp_chord_notes.append(temp_chord_notes[-1] + 10)
                            if random.random() < 0.4: # 40% chance de adicionar 9
                                if (temp_chord_notes[-1] + 14) <= 100: temp_chord_notes.append(temp_chord_notes[-1] + 14)
                        chord_notes = sorted(list(set(temp_chord_notes))) # Remove duplicatas e ordena

                # Adiciona inversões ou voicings variados
                if random.random() < 0.4 and len(chord_notes) >= 3: # 40% de chance de inversão para Liquid Funk
                    inversion_type = random.choice(['first', 'second'])
                    if inversion_type == 'first':
                        chord_notes = [chord_notes[1], chord_notes[2], chord_notes[0] + 12]
                    elif inversion_type == 'second':
                        chord_notes = [chord_notes[2], chord_notes[0] + 12, chord_notes[1] + 12]
                    chord_notes.sort()

                for note in chord_notes:
                    chord_events.append(('note_on', note, velocity, int(chords_ticks_elapsed)))
                    chord_events.append(('note_off', note, velocity, int(chords_ticks_elapsed + int(chord_duration_ticks * note_off_factor))))
                log_text_local += f"CHORDS/PADS: Chord {chord_symbol} at {int(chords_ticks_elapsed)} for {chord_duration_ticks} ticks\n"
                chords_ticks_elapsed += ticks_per_beat * 4
            if chords_ticks_elapsed >= total_ticks: break
        log_text += log_text_local

    def _generate_lead_melody(self, lead_events, total_ticks, ticks_per_beat, log_text,
                              root_note_midi, scale_type, progression_chords, style_data, music_style):
        lead_ticks_elapsed = 0
        log_text_local = "\n--- Lead Melody ---\n"
        lead_octave = style_data.get('lead_octave_offset', 0)
        full_scale_notes_lead_octave = self._get_scale_notes(root_note_midi, scale_type, octave_offset=lead_octave)
        num_chord_beats = ticks_per_beat * 4

        num_chord_cycles = (total_ticks // num_chord_beats) + 1

        for cycle_idx in range(num_chord_cycles):
            for chord_symbol in progression_chords:
                if lead_ticks_elapsed >= total_ticks: break

                chord_notes_for_lead = self._get_chord_midi_notes(root_note_midi, scale_type, chord_symbol, octave_offset=lead_octave)

                if not chord_notes_for_lead: continue # Evita erro se o acorde não tiver notas válidas

                if music_style == 'Liquid Funk':
                    if random.random() < 0.2: # Menor chance de ter melodia contínua, mais espaçada
                        lead_ticks_elapsed += num_chord_beats
                        continue

                    # Prioriza notas mais longas e melódicas
                    num_notes_in_block = random.randint(1, 4) # Mais variação, ainda tendendo a menos notas por bloco
                    note_duration_options = [
                        ticks_per_beat, # Semínima
                        ticks_per_beat // 2, # Colcheia
                        int(ticks_per_beat * 1.5), # Semínima pontuada
                        ticks_per_beat * 2 # Mínima
                    ]
                    if random.random() < 0.2: # Pequena chance de semicolcheias para preenchimentos
                        note_duration_options.append(ticks_per_beat // 4)
                    velocity = random.randint(85, 115) # Mais expressiva
                    note_off_factor = random.uniform(0.9, 0.98) # Mais legato

                elif music_style == 'Drum and Bass':
                    if random.random() < 0.7:
                        lead_ticks_elapsed += num_chord_beats
                        continue

                    num_notes_in_block = random.randint(1, 3)
                    note_duration_options = [ticks_per_beat // 2, ticks_per_beat // 4]
                    velocity = random.randint(80, 110)
                    note_off_factor = 0.9 # Mais cortado

                else:
                    num_notes_in_block = random.randint(2, 5)
                    note_duration_options = [self.ticks_per_beat, self.ticks_per_beat // 2, int(self.ticks_per_beat * 0.75)]
                    if random.random() < 0.3:
                        note_duration_options.append(self.ticks_per_beat // 4)
                    velocity = random.randint(90, 120)
                    note_off_factor = 0.9

                for _ in range(num_notes_in_block):
                    if lead_ticks_elapsed >= total_ticks: break

                    # Preferência por notas do acorde, mas com chance de notas da escala para melodia
                    current_note = random.choice(chord_notes_for_lead) if random.random() < 0.6 else random.choice(full_scale_notes_lead_octave)

                    # Variação de oitava mais controlada
                    if random.random() < 0.15: # 15% de chance de mudar uma oitava acima ou abaixo
                        if current_note + 12 <= 100: current_note += 12
                        elif current_note - 12 >= 30: current_note -= 12

                    note_duration = random.choice(note_duration_options)
                    min_duration = ticks_per_beat // 8
                    note_duration = max(note_duration, min_duration)

                    lead_events.append(('note_on', current_note, velocity, int(lead_ticks_elapsed)))
                    lead_events.append(('note_off', current_note, velocity, int(lead_ticks_elapsed + int(note_duration * note_off_factor))))
                    log_text_local += f"LEAD: Note {current_note} (MIDI) at {int(lead_ticks_elapsed)} for {int(note_duration * note_off_factor)} ticks\n"

                    lead_ticks_elapsed += note_duration

                if lead_ticks_elapsed % num_chord_beats != 0:
                    lead_ticks_elapsed = ((lead_ticks_elapsed // num_chord_beats) + 1) * num_chord_beats
            if lead_ticks_elapsed >= total_ticks: break
        log_text += log_text_local


    def _generate_arpeggio(self, arpeggio_events, total_ticks, ticks_per_beat, log_text,
                           root_note_midi, scale_type, progression_chords, style_data, music_style):
        arpeggio_ticks_elapsed = 0
        log_text_local = "\n--- Arpeggio ---\n"
        arpeggio_octave = style_data.get('arpeggio_octave_offset', 0)

        num_chord_cycles = (total_ticks // (ticks_per_beat * 4)) + 1

        for cycle_idx in range(num_chord_cycles):
            for chord_symbol in progression_chords:
                if arpeggio_ticks_elapsed >= total_ticks: break

                chord_notes_for_arpeggio = self._get_chord_midi_notes(root_note_midi, scale_type, chord_symbol, octave_offset=arpeggio_octave)

                if not chord_notes_for_arpeggio: continue

                if music_style == 'Liquid Funk':
                    arpeggio_note_duration = ticks_per_beat // random.choice([2, 4]) # 1/8 ou 1/16, mais rápido que o padrão
                    min_arpeggio_duration = ticks_per_beat // 16 # Mínimo de 1/16 para Liquid Funk
                    arpeggio_note_duration = max(arpeggio_note_duration, min_arpeggio_duration)
                    velocity = random.randint(70, 95) # Mais suave para arpejos de fundo
                    note_off_factor = random.uniform(0.8, 0.95) # Mais sustain/legato

                else:
                    arpeggio_note_duration = ticks_per_beat // random.choice([2, 4])
                    min_arpeggio_duration = ticks_per_beat // 8
                    arpeggio_note_duration = max(arpeggio_note_duration, min_arpeggio_duration)
                    velocity = 90
                    note_off_factor = 0.8

                arpeggio_direction = random.choice(['up', 'down', 'up_down', 'random'])

                notes_to_arpeggiate = sorted(chord_notes_for_arpeggio)

                extended_notes = list(notes_to_arpeggiate)
                # Adiciona notas de oitava para arpejos mais amplos (comuns em Liquid Funk)
                for note in notes_to_arpeggiate:
                    if note + 12 <= 100: extended_notes.append(note + 12)
                    if note - 12 >= 30: extended_notes.insert(0, note - 12) # Adiciona oitava abaixo também
                extended_notes = sorted(list(set(extended_notes)))

                for beat_in_chord in range(4): # Arpeja por beat no bloco de acorde
                    if arpeggio_ticks_elapsed >= total_ticks: break

                    current_pattern_notes = []
                    if arpeggio_direction == 'up':
                        current_pattern_notes = extended_notes
                    elif arpeggio_direction == 'down':
                        current_pattern_notes = list(reversed(extended_notes))
                    elif arpeggio_direction == 'up_down':
                        current_pattern_notes = extended_notes + list(reversed(extended_notes[1:-1]))
                    else: # 'random'
                        current_pattern_notes = random.sample(extended_notes, len(extended_notes))

                    # Gerar um ciclo completo do arpejo por "sub-bloco" para garantir que ele toque o acorde
                    for note in current_pattern_notes:
                        if arpeggio_ticks_elapsed >= total_ticks: break
                        arpeggio_events.append(('note_on', note, velocity, int(arpeggio_ticks_elapsed)))
                        arpeggio_events.append(('note_off', note, velocity, int(arpeggio_ticks_elapsed + int(arpeggio_note_duration * note_off_factor))))
                        arpeggio_ticks_elapsed += arpeggio_note_duration
            if arpeggio_ticks_elapsed >= total_ticks: break
        log_text += log_text_local

    def _generate_drums(self, drum_events, total_ticks, ticks_per_beat, log_text, music_style):
        DRUM_NOTES = {
            'kick': 36,  # Bass Drum 1
            'snare': 38, # Acoustic Snare
            'clap': 39,  # Hand Clap (sometimes used instead of or with snare)
            'hi_hat_closed': 42, # Closed Hi-Hat
            'hi_hat_open': 46,   # Open Hi-Hat
            'ride': 51,  # Ride Cymbal 1
            'crash': 49  # Crash Cymbal 1
        }

        drum_ticks_elapsed = 0
        log_text_local = "\n--- Drums ---\n"

        # Define as durações em ticks para clareza
        tick_32nd = ticks_per_beat // 8
        tick_16th = ticks_per_beat // 4
        tick_8th = ticks_per_beat // 2
        tick_quarter = ticks_per_beat # Semínima (1 beat)
        tick_half = ticks_per_beat * 2 # Mínima (2 beats)

        while drum_ticks_elapsed < total_ticks:
            if music_style == 'Drum and Bass' or music_style == 'Liquid Funk':
                log_text_local += f"Gerando bateria estilo {music_style} (DNB padrão Tum-Tá-Tum-Tá com Kick 3.5)\n"

                # BEAT 1: Kick forte
                drum_events.append(('note_on', DRUM_NOTES['kick'], random.randint(100, 120), int(drum_ticks_elapsed)))
                drum_events.append(('note_off', DRUM_NOTES['kick'], 0, int(drum_ticks_elapsed + tick_8th * 0.9)))

                # BEAT 2: Snare forte
                snare_velocity = random.randint(110, 127)
                drum_events.append(('note_on', DRUM_NOTES['snare'], snare_velocity, int(drum_ticks_elapsed + tick_quarter)))
                drum_events.append(('note_off', DRUM_NOTES['snare'], 0, int(drum_ticks_elapsed + tick_quarter + tick_8th * 0.9)))

                # BEAT 3.5: Kick forte (na metade do terceiro beat)
                kick_3_5_pos = drum_ticks_elapsed + (tick_quarter * 2) + tick_8th # Beat 3 + colcheia (3 e)
                drum_events.append(('note_on', DRUM_NOTES['kick'], random.randint(90, 110), int(kick_3_5_pos)))
                drum_events.append(('note_off', DRUM_NOTES['kick'], 0, int(kick_3_5_pos + tick_8th * 0.9)))

                # BEAT 4: Snare forte
                drum_events.append(('note_on', DRUM_NOTES['snare'], snare_velocity, int(drum_ticks_elapsed + tick_quarter * 3)))
                drum_events.append(('note_off', DRUM_NOTES['snare'], 0, int(drum_ticks_elapsed + tick_quarter * 3 + tick_8th * 0.9)))

                # --- Variações de Kick Sincopado (preenchimento, sem competir com 1 e 3.5) ---
                # Kick no "e" do 1 (1 e & a 2)
                if random.random() < 0.4: # 40% de chance para um kick mais sutil
                    kick_pos_1_e = drum_ticks_elapsed + tick_8th # (1 e)
                    if kick_pos_1_e < total_ticks:
                        drum_events.append(('note_on', DRUM_NOTES['kick'], random.randint(60, 80), int(kick_pos_1_e))) # Velocity menor
                        drum_events.append(('note_off', DRUM_NOTES['kick'], 0, int(kick_pos_1_e + tick_8th * 0.7)))

                # Kick no "a" do 2 (2 e & a 3) - antes do snare do 2.5
                if random.random() < 0.2: # Menor chance, mais sutil
                    kick_pos_2_a = drum_ticks_elapsed + tick_quarter + tick_16th * 3 # (2 e & a)
                    if kick_pos_2_a < total_ticks:
                        drum_events.append(('note_on', DRUM_NOTES['kick'], random.randint(50, 70), int(kick_pos_2_a)))
                        drum_events.append(('note_off', DRUM_NOTES['kick'], 0, int(kick_pos_2_a + tick_8th * 0.6)))

                # --- Hi-Hats de preenchimento (mais consistentes) ---
                # Hi-hats em semicolcheias para o groove "shuffling"
                for i in range(16): # 16 semicolcheias por compasso
                    hi_hat_pos_16th = drum_ticks_elapsed + (i * tick_16th)
                    if hi_hat_pos_16th < total_ticks:
                        vel = random.randint(55, 80) # Variação suave de velocity

                        # Prioridade para hi-hat fechado na semicolcheia
                        drum_events.append(('note_on', DRUM_NOTES['hi_hat_closed'], vel, int(hi_hat_pos_16th)))
                        drum_events.append(('note_off', DRUM_NOTES['hi_hat_closed'], 0, int(hi_hat_pos_16th + tick_16th * 0.4))) # Curto e percussivo

                        # Hi-hat aberto em posições específicas (mais espaçado)
                        if i == 7 or i == 15: # No final do Beat 2 e Beat 4
                             if random.random() < 0.25: # Menor chance para aberto
                                drum_events.append(('note_on', DRUM_NOTES['hi_hat_open'], random.randint(65, 85), int(hi_hat_pos_16th)))
                                drum_events.append(('note_off', DRUM_NOTES['hi_hat_open'], 0, int(hi_hat_pos_16th + tick_8th * 0.6))) # Mais sustain

                # --- Fills de Bateria (no final de 4 compassos ou 8 compassos) ---
                current_measure = int(drum_ticks_elapsed / (ticks_per_beat * 4))

                if (current_measure + 1) % 4 == 0 and random.random() < 0.7: # Forte chance no final do 4º compasso
                    fill_start_tick = drum_ticks_elapsed + tick_quarter * 3 # Início do último beat do compasso
                    fill_duration_ticks = tick_quarter # Duração de um beat

                    fill_choices = ['snare_roll', 'kick_snare_combo_fill', 'hihat_snare_quick_fill']
                    chosen_fill = random.choice(fill_choices)

                    if chosen_fill == 'snare_roll':
                        roll_notes = random.randint(4, 8)
                        roll_note_duration = tick_16th if roll_notes <= 4 else tick_32nd
                        for i in range(roll_notes):
                            if fill_start_tick + (i * roll_note_duration) < total_ticks:
                                drum_events.append(('note_on', DRUM_NOTES['snare'], random.randint(70, 95), int(fill_start_tick + (i * roll_note_duration))))
                                drum_events.append(('note_off', DRUM_NOTES['snare'], 0, int(fill_start_tick + (i * roll_note_duration) + roll_note_duration * 0.8)))

                    elif chosen_fill == 'kick_snare_combo_fill':
                        if fill_start_tick < total_ticks:
                            drum_events.append(('note_on', DRUM_NOTES['kick'], random.randint(90, 110), int(fill_start_tick)))
                            drum_events.append(('note_off', DRUM_NOTES['kick'], 0, int(fill_start_tick + tick_16th * 0.8)))
                            if fill_start_tick + tick_16th * 2 < total_ticks:
                                drum_events.append(('note_on', DRUM_NOTES['snare'], random.randint(90, 110), int(fill_start_tick + tick_16th * 2)))
                                drum_events.append(('note_off', DRUM_NOTES['snare'], 0, int(fill_start_tick + tick_16th * 2 + tick_16th * 0.8)))
                            if fill_start_tick + tick_16th * 3 < total_ticks:
                                drum_events.append(('note_on', DRUM_NOTES['kick'], random.randint(70, 90), int(fill_start_tick + tick_16th * 3)))
                                drum_events.append(('note_off', DRUM_NOTES['kick'], 0, int(fill_start_tick + tick_16th * 3 + tick_16th * 0.8)))

                    elif chosen_fill == 'hihat_snare_quick_fill':
                        for i in range(3):
                            if fill_start_tick + (i * tick_16th) < total_ticks:
                                drum_events.append(('note_on', DRUM_NOTES['hi_hat_closed'], random.randint(60, 80), int(fill_start_tick + (i * tick_16th))))
                                drum_events.append(('note_off', DRUM_NOTES['hi_hat_closed'], 0, int(fill_start_tick + (i * tick_16th) + tick_16th * 0.5)))
                        if fill_start_tick + tick_16th * 3 < total_ticks:
                            drum_events.append(('note_on', DRUM_NOTES['snare'], random.randint(90, 110), int(fill_start_tick + tick_16th * 3)))
                            drum_events.append(('note_off', DRUM_NOTES['snare'], 0, int(fill_start_tick + tick_16th * 3 + tick_16th * 0.8)))

                # Avança para o próximo compasso (4 beats)
                drum_ticks_elapsed += ticks_per_beat * 4

            else: # Lógica de bateria genérica para outros estilos (mantida como está)
                log_text_local += f"Gerando bateria estilo {music_style} (padrão básico)\n"
                # Kick no 1 e 3
                drum_events.append(('note_on', DRUM_NOTES['kick'], random.randint(95, 110), int(drum_ticks_elapsed)))
                drum_events.append(('note_off', DRUM_NOTES['kick'], 0, int(drum_ticks_elapsed + ticks_per_beat // 4)))

                drum_events.append(('note_on', DRUM_NOTES['kick'], random.randint(95, 110), int(drum_ticks_elapsed + ticks_per_beat * 2)))
                drum_events.append(('note_off', DRUM_NOTES['kick'], 0, int(drum_ticks_elapsed + ticks_per_beat * 2 + ticks_per_beat // 4)))

                # Snare no 2 e 4
                drum_events.append(('note_on', DRUM_NOTES['snare'], random.randint(85, 100), int(drum_ticks_elapsed + ticks_per_beat)))
                drum_events.append(('note_off', DRUM_NOTES['snare'], 0, int(drum_ticks_elapsed + ticks_per_beat + ticks_per_beat // 4)))

                drum_events.append(('note_on', DRUM_NOTES['snare'], random.randint(85, 100), int(drum_ticks_elapsed + ticks_per_beat * 3)))
                drum_events.append(('note_off', DRUM_NOTES['snare'], 0, int(drum_ticks_elapsed + ticks_per_beat * 3 + ticks_per_beat // 4)))

                # Hi-hats em colcheias
                for i in range(0, 4):
                    drum_events.append(('note_on', DRUM_NOTES['hi_hat_closed'], random.randint(60, 80), int(drum_ticks_elapsed + i * ticks_per_beat // 2)))
                    drum_events.append(('note_off', DRUM_NOTES['hi_hat_closed'], 0, int(drum_ticks_elapsed + i * ticks_per_beat // 2 + ticks_per_beat // 8)))

                drum_ticks_elapsed += ticks_per_beat * 4
        log_text += log_text_local

    def save_midi_file(self, all_midi_events, filename, bpm):
        mid = mido.MidiFile(ticks_per_beat=self.ticks_per_beat)
        mid.tempo = mido.bpm2tempo(bpm)

        track_map = {
            'bass': {'track_num': 0, 'channel': 0},
            'chords': {'track_num': 1, 'channel': 1},
            'lead': {'track_num': 2, 'channel': 2},
            'pads': {'track_num': 3, 'channel': 3},
            'arpeggio': {'track_num': 4, 'channel': 4},
            'drums': {'track_num': 5, 'channel': 9} # Canal 9 é o canal de percussão MIDI padrão
        }

        for part_name, part_data in track_map.items():
            if part_name in all_midi_events and all_midi_events[part_name]:
                track = mido.MidiTrack()
                mid.tracks.append(track)
                track.name = part_name.capitalize()

                # Atribuição de programas (instrumentos)
                if part_name == 'bass':
                    track.append(mido.Message('program_change', program=33, time=0)) # Electric Bass (finger)
                elif part_name == 'chords':
                    track.append(mido.Message('program_change', program=1, time=0)) # Bright Acoustic Piano
                elif part_name == 'lead':
                    track.append(mido.Message('program_change', program=81, time=0)) # Lead (Square)
                elif part_name == 'pads':
                    track.append(mido.Message('program_change', program=89, time=0)) # Pad (New Age)
                elif part_name == 'arpeggio':
                    track.append(mido.Message('program_change', program=81, time=0)) # Lead (Square)

                events = all_midi_events[part_name]
                events.sort(key=lambda x: x[3]) # Garante que os eventos estejam em ordem cronológica
                
                current_ticks = 0
                for event_type, note, velocity, time in events:
                    delta_time = time - current_ticks # Calcula o tempo delta
                    
                    # Evita delta_time negativo, caso haja algum erro na ordenação ou eventos no mesmo tick
                    if delta_time < 0: delta_time = 0 

                    # Garante que delta_time é um inteiro antes de adicionar à mensagem MIDI
                    track.append(mido.Message(event_type, channel=part_data['channel'], note=note, velocity=velocity, time=int(delta_time)))
                    current_ticks = time # Atualiza o tempo atual para o próximo cálculo de delta

        mid.save(filename)