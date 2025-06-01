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
            },
            'Minor Harmonic': { # Menor Harmônica
                'intervals': [0, 2, 3, 5, 7, 8, 11],
                'chords': { # Acordes comuns na harmônica, adaptados da natural
                    'i': [0, 3, 7],
                    'ii°': [2, 5, 8],
                    'III+': [3, 7, 11], # Aumentado
                    'iv': [5, 8, 12],
                    'V': [7, 11, 14], # Dominante
                    'VI': [8, 12, 15],
                    'vii°': [11, 14, 17]
                }
            },
            'Minor Melodic': { # Menor Melódica (ascendente)
                'intervals': [0, 2, 3, 5, 7, 9, 11],
                'chords': { # Pode usar os da Maior ou adaptar
                    'i': [0, 3, 7],
                    'ii': [2, 5, 9],
                    'III+': [3, 7, 11],
                    'IV': [5, 9, 12],
                    'V': [7, 11, 14],
                    'vi°': [9, 12, 15], # Diminuto
                    'vii°': [11, 14, 17]
                }
            },
            'Pentatonic Major': { # Pentatônica Maior
                'intervals': [0, 2, 4, 7, 9],
                'chords': { # Usa acordes simples como I, IV, V da maior
                    'I': [0, 4, 7],
                    'IV': [5, 9, 12],
                    'V': [7, 11, 14]
                }
            },
            'Pentatonic Minor': { # Pentatônica Menor
                'intervals': [0, 3, 5, 7, 10],
                'chords': { # Usa acordes simples como i, iv, v da menor
                    'i': [0, 3, 7],
                    'iv': [5, 8, 12],
                    'v': [7, 10, 14]
                }
            },
            'Blues Minor': { # Blues Menor (Pentatônica Menor + b5)
                'intervals': [0, 3, 5, 6, 7, 10], # 0, b3, 4, b5, 5, b7
                'chords': { # Geralmente sobre acordes dominantes ou acordes da menor
                    'i': [0, 3, 7],
                    'IV7': [5, 9, 12, 15], # Exemplo de acorde 7
                    'V7': [7, 11, 14, 17]
                }
            },
            'Blues Major': { # Blues Maior (Pentatônica Maior + b3)
                'intervals': [0, 2, 3, 4, 7, 9], # 0, 2, b3, 3, 5, 6
                'chords': { # Geralmente sobre acordes dominantes ou acordes da maior
                    'I': [0, 4, 7],
                    'IV7': [5, 9, 12, 15],
                    'V7': [7, 11, 14, 17]
                }
            },
            'Chromatic': { # Cromática (todas as notas)
                'intervals': [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
                'chords': { # Não tem acordes diatônicos fixos; pode usar acordes de passagem ou basear-se na maior/menor
                    'Cmaj': [0, 4, 7], # Exemplo para ter uma referência
                    'Cmin': [0, 3, 7]
                }
            },
            # Modos Gregos (baseados na escala maior)
            'Ionian': { # Jônio (Maior)
                'intervals': [0, 2, 4, 5, 7, 9, 11],
                'chords': {
                    'I': [0, 4, 7], 'ii': [2, 5, 9], 'iii': [4, 7, 11],
                    'IV': [5, 9, 12], 'V': [7, 11, 14], 'vi': [9, 12, 16], 'vii°': [11, 14, 17]
                }
            },
            'Dorian': { # Dórico (Maior com b3, b7) - Modo menor
                'intervals': [0, 2, 3, 5, 7, 9, 10],
                'chords': {
                    'i': [0, 3, 7], 'ii': [2, 5, 9], 'III': [3, 7, 10],
                    'IV': [5, 9, 12], 'v': [7, 10, 14], 'vi°': [9, 12, 15], 'VII': [10, 14, 17]
                }
            },
            'Phrygian': { # Frígio (Maior com b2, b3, b6, b7) - Modo menor
                'intervals': [0, 1, 3, 5, 7, 8, 10],
                'chords': {
                    'i': [0, 3, 7], 'II°': [1, 5, 8], 'III': [3, 7, 10],
                    'iv': [5, 8, 12], 'v°': [7, 10, 13], 'VI': [8, 12, 15], 'vii': [10, 13, 17]
                }
            },
            'Lydian': { # Lídio (Maior com #4) - Modo maior
                'intervals': [0, 2, 4, 6, 7, 9, 11],
                'chords': {
                    'I': [0, 4, 7], 'II': [2, 6, 9], 'iii': [4, 7, 11],
                    'IV+': [6, 9, 12], 'V': [7, 11, 14], 'vi': [9, 12, 16], 'vii°': [11, 14, 17]
                }
            },
            'Mixolydian': { # Mixolídio (Maior com b7) - Modo dominante
                'intervals': [0, 2, 4, 5, 7, 9, 10],
                'chords': {
                    'I': [0, 4, 7], 'ii°': [2, 5, 8], 'iii°': [4, 7, 10],
                    'IV': [5, 9, 12], 'v': [7, 10, 14], 'vi°': [9, 12, 15], 'VII': [10, 14, 17]
                }
            },
            'Aeolian': { # Eólio (Menor Natural)
                'intervals': [0, 2, 3, 5, 7, 8, 10],
                'chords': {
                    'i': [0, 3, 7], 'ii°': [2, 5, 8], 'III': [3, 7, 10],
                    'iv': [5, 8, 12], 'v': [7, 10, 14], 'VI': [8, 12, 15], 'VII': [10, 14, 17]
                }
            },
            'Locrian': { # Lócrio (Maior com b2, b3, b5, b6, b7) - Modo diminuto
                'intervals': [0, 1, 3, 5, 6, 8, 10],
                'chords': {
                    'i°': [0, 3, 6], 'IIb': [1, 5, 8], 'IIIb': [3, 6, 10],
                    'iv°': [5, 8, 11], 'Vb': [6, 10, 13], 'VIb': [8, 11, 15], 'VIIb': [10, 13, 17]
                }
            },
            # Escalas Bebop (geralmente usadas para improvisação sobre acordes dominantes)
            'Bebop Major': { # Major Bebop (Maior com #5)
                'intervals': [0, 2, 4, 5, 7, 8, 9, 11], # Adiciona a b6 (F# em C) entre 5 e 6
                'chords': { # Pode usar os da Major como base
                    'I': [0, 4, 7], 'V7': [7, 11, 14, 17]
                }
            },
            'Bebop Dominant': { # Dominant Bebop (Mixolídio com #5)
                'intervals': [0, 2, 4, 5, 7, 8, 10, 11], # Adiciona a 7M (B em C)
                'chords': { # Ideal para acordes Dominantes
                    'V7': [7, 11, 14, 17]
                }
            },
            'Bebop Minor': { # Minor Bebop (Dórico com #7)
                'intervals': [0, 2, 3, 5, 7, 9, 10, 11], # Adiciona a 7M (B em C)
                'chords': { # Ideal para acordes Menores
                    'i': [0, 3, 7]
                }
            },
            'Bebop Dorian': { # Bebop Dorian (Dórico com #7) - igual ao Bebop Minor
                'intervals': [0, 2, 3, 5, 7, 9, 10, 11],
                'chords': {
                    'i': [0, 3, 7]
                }
            },
            'Bebop Melodic Minor': { # Menor Melódica com #7
                'intervals': [0, 2, 3, 5, 7, 9, 10, 11],
                'chords': {
                    'i': [0, 3, 7]
                }
            },
             'Bebop Phrygian Dominant': { # Phrygian Dominant (Frígio com b2, b3, 5, b6, b7) - também chamada de 5º modo da Menor Harmônica
                'intervals': [0, 1, 4, 5, 7, 8, 10], # 0, b2, 3, 4, 5, b6, b7
                'chords': {
                    'V7': [7, 11, 14, 17] # Ideal para acordes V7 com 9b e 13b
                }
            }
        }
        self.root_notes = {
            'C': 60, 'C#': 61, 'D': 62, 'D#': 63, 'E': 64, 'F': 65,
            'F#': 66, 'G': 67, 'G#': 68, 'A': 69, 'A#': 70, 'B': 71
        }
        self.instrument_channels = {
            'bass': {'channel': 0, 'program': 33}, # Electric Bass (finger)
            'chords': {'channel': 1, 'program': 1}, # Bright Acoustic Piano
            'lead': {'channel': 2, 'program': 81}, # Lead (Square)
            'pads': {'channel': 3, 'program': 89}, # Pad (New Age)
            'arpeggio': {'channel': 4, 'program': 81}, # Lead (Square)
            'drums': {'channel': 9, 'program': 0} # Drums (General MIDI Percussion)
        }
        self.ticks_per_beat = 480 # Resolução MIDI (pulsos por semínima)

    def note_to_midi(self, note_name, octave):
        """Converte o nome da nota (C, C#, D...) e oitava em um número MIDI."""
        notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        note_val = notes.index(note_name)
        return note_val + (octave * 12)

    def get_scale_notes(self, root_key_str, scale_intervals):
        root_midi = self.root_notes[root_key_str]
        return [root_midi + interval for interval in scale_intervals]

    def generate_music_parts(self, root_key_str, scale_type, bpm, num_beats,
                             generate_bass, generate_chords, generate_lead, generate_pads,
                             generate_arpeggio, generate_drums, music_style):
        
        all_midi_events = {}
        log_text = ""
        
        root_midi = self.root_notes[root_key_str]
        
        # Obter intervalos da escala selecionada
        if scale_type not in self.scales:
            log_text += f"ERRO: Escala '{scale_type}' não encontrada. Usando 'Major' como fallback.\n"
            scale_type = 'Major'
            
        scale_intervals = self.scales[scale_type]['intervals']
        scale_notes = self.get_scale_notes(root_key_str, scale_intervals)
        
        # Determinar a progressão de acordes.
        # Para escalas que não têm um conjunto de acordes diatônicos "comuns",
        # podemos usar uma progressão de acordes baseada em Maior ou Menor
        # e aplicar a escala no fraseado das partes melódicas (lead, arpejo, bass).
        
        # Abordagem: Se a escala selecionada tem acordes definidos, use-os.
        # Caso contrário, fallback para uma progressão maior ou menor.
        
        available_chords = self.scales[scale_type].get('chords', {})
        chord_progression_keys = []

        if available_chords:
            # Tenta usar uma progressão diatônica comum para a escala, se disponível
            if scale_type in ['Major', 'Ionian', 'Lydian', 'Mixolydian', 'Bebop Major', 'Bebop Dominant']:
                chord_progression_keys = ['I', 'vi', 'IV', 'V']
                if 'V7' in available_chords: # Preferir V7 para escalas dominantes
                    chord_progression_keys = ['I', 'vi', 'IV', 'V7']
            elif scale_type in ['Minor', 'Aeolian', 'Dorian', 'Phrygian', 'Minor Harmonic', 'Minor Melodic', 'Bebop Minor', 'Bebop Dorian', 'Bebop Melodic Minor']:
                chord_progression_keys = ['i', 'VI', 'VII', 'VII'] # Common minor progression
                if 'III' in available_chords and 'VII' in available_chords:
                     chord_progression_keys = ['i', 'VI', 'III', 'VII']
            elif scale_type in ['Pentatonic Major']:
                chord_progression_keys = ['I', 'IV', 'V']
            elif scale_type in ['Pentatonic Minor']:
                chord_progression_keys = ['i', 'iv', 'v']
            elif scale_type in ['Blues Major', 'Blues Minor']:
                chord_progression_keys = ['I', 'IV7', 'V7', 'IV7'] # Progressão de blues
            elif scale_type == 'Chromatic': # Cromática não tem progressão diatônica óbvia
                chord_progression_keys = ['Cmaj', 'Cmin'] # Apenas exemplos, talvez não sejam usados como progressão
        
        # Fallback se a progressão não foi definida ou se a escala não tem 'chords'
        if not chord_progression_keys:
            if scale_type == 'Major' or 'Major' in scale_type or 'Ionian' in scale_type or 'Lydian' in scale_type or 'Mixolydian' in scale_type:
                chord_progression_keys = ['I', 'vi', 'IV', 'V']
                available_chords = self.scales['Major']['chords'] # Usar acordes da maior como fallback
            else: # Para qualquer outra escala sem progressão específica (incluindo Chromatic, Locrian, etc.)
                chord_progression_keys = ['i', 'VI', 'VII', 'VII']
                available_chords = self.scales['Minor']['chords'] # Usar acordes da menor como fallback
            log_text += f"Usando progressão de acordes baseada em {('Major' if 'Major' in scale_type else 'Minor')} para '{scale_type}'.\n"

        chords_data = []
        for chord_key in chord_progression_keys:
            if chord_key in available_chords:
                chords_data.append(available_chords[chord_key])
            else:
                # Fallback para acordes de C Major ou A Minor se o acorde específico não existir na escala
                if chord_key.startswith('I') or chord_key.startswith('IV') or chord_key.startswith('V'):
                    chords_data.append(self.scales['Major']['chords'].get(chord_key, [0,4,7])) # Default Cmaj
                else:
                    chords_data.append(self.scales['Minor']['chords'].get(chord_key, [0,3,7])) # Default Amin

        # Convert chord intervals to actual MIDI notes based on root
        progression_midi_notes = []
        for i, chord_intervals in enumerate(chords_data):
            # Base do acorde na tônica da música. Poderia ser o grau da escala, mas simplificamos para a tônica
            # para as escalas mais complexas, onde as progressões diatônicas são menos óbvias.
            base_note_for_chord = root_midi
            
            # Para acordes que são explicitamente de um grau da escala (como 'ii', 'VI'),
            # vamos tentar usar o grau da escala se for uma escala com estrutura de acordes diatônicos claros.
            # Se for uma escala "exótica" como Blues ou Bebop, ou Cromática, a base será a tônica da música.
            
            # Esta lógica é uma simplificação. Em um gerador mais avançado,
            # a geração de acordes deveria ser mais inteligente para cada escala.
            
            progression_midi_notes.append([base_note_for_chord + interval for interval in chord_intervals])
        
        # Adjusting num_beats to be a multiple of 4 for consistent loop (4 beats per measure)
        num_measures = num_beats // 4
        if num_beats % 4 != 0:
            num_beats = num_measures * 4
            log_text += f"A duração foi ajustada para {num_beats} batidas ({num_measures} compassos) para consistência.\n"

        # Calculate total ticks and us_per_beat for mido file saving and visualization
        us_per_beat = mido.bpm2tempo(bpm)
        total_ticks = mido.second2tick((num_beats / bpm) * 60, self.ticks_per_beat, us_per_beat)

        # Passar a escala_intervals e a lista de notas da escala para as funções de geração
        if generate_bass:
            # Bass agora recebe a escala_intervals para variar as notas
            all_midi_events['bass'] = self.generate_bass_line(root_key_str, scale_intervals, num_beats)
            log_text += "Linha de Baixo gerada.\n"
        
        if generate_chords:
            # Acordes agora recebem a progressão_midi_notes já calculada
            all_midi_events['chords'] = self.generate_chords(num_beats, progression_midi_notes)
            log_text += "Acordes gerados.\n"
            
        if generate_lead:
            # Lead agora recebe a escala_intervals para variar as notas
            all_midi_events['lead'] = self.generate_lead_melody(root_key_str, scale_intervals, num_beats)
            log_text += "Melodia Principal gerada.\n"
        
        if generate_pads:
            # Pads agora recebem a progressão_midi_notes já calculada
            all_midi_events['pads'] = self.generate_pads(num_beats, progression_midi_notes)
            log_text += "Pads gerados.\n"

        if generate_arpeggio:
            # Arpejo agora recebe a progressão_midi_notes já calculada
            all_midi_events['arpeggio'] = self.generate_arpeggio(num_beats, progression_midi_notes)
            log_text += "Arpejo gerado.\n"

        if generate_drums:
            all_midi_events['drums'] = self.generate_drums(num_beats)
            log_text += "Bateria gerada.\n"

        if not all_midi_events:
            log_text += "Nenhuma parte musical selecionada para geração.\n"

        return all_midi_events, log_text, total_ticks, us_per_beat

    def generate_bass_line(self, root_key_str, scale_intervals, num_beats):
        events = []
        root_midi = self.root_notes[root_key_str]
        # Oitava mais baixa para o baixo, garantindo que a nota esteja em uma faixa MIDI válida
        scale_notes = [root_midi + interval - 12 for interval in scale_intervals if (root_midi + interval - 12) >= 24]
        
        current_tick = 0
        
        # Define a menor unidade de quantização para o baixo (ex: semicolcheia)
        quantization_unit = self.ticks_per_beat // 4 # Semicolcheia (120 ticks)
        
        # Velocities para groove e expressividade
        base_velocity = 85
        velocity_range = 15 # Variação de +/- 15 da base

        for beat_num in range(num_beats):
            # A base do baixo sempre começa na batida (semínima)
            beat_start_tick = beat_num * self.ticks_per_beat
            
            # Escolhe uma nota da escala para a batida principal
            bass_note = random.choice(scale_notes)
            
            # Decide o ritmo da nota principal (semínima, colcheia, pontuada)
            # Mais variedade rítmica para o baixo
            rhythmic_options = [
                (self.ticks_per_beat, 1), # Semínima
                (self.ticks_per_beat // 2, 2), # Colcheia
                (int(self.ticks_per_beat * 1.5), 0.75), # Semínima pontuada
                (self.ticks_per_beat * 2, 0.5) # Mínima
            ]
            duration_ticks, _ = random.choice(rhythmic_options)
            
            # Garante que a duração seja um múltiplo da unidade de quantização
            duration_ticks = (duration_ticks // quantization_unit) * quantization_unit
            if duration_ticks == 0: duration_ticks = quantization_unit # Evita duração zero

            # Velocity com variação para humanizar
            velocity = random.randint(base_velocity - velocity_range, base_velocity + velocity_range)
            
            # Adiciona a nota principal
            events.append(('note_on', bass_note, velocity, beat_start_tick))
            # Pequeno release para evitar sobreposição
            events.append(('note_off', bass_note, 0, beat_start_tick + duration_ticks - (quantization_unit // 2)))

            # Chance de adicionar notas extras em subdivisões (colcheias/semicolcheias) para groove
            current_sub_tick = beat_start_tick + duration_ticks # Começa após a nota principal
            
            while current_sub_tick < beat_start_tick + self.ticks_per_beat: # Dentro da mesma batida
                if random.random() < 0.6: # 60% de chance de adicionar uma nota extra
                    sub_note_duration = random.choice([quantization_unit, quantization_unit * 2]) # Semicolcheia ou Colcheia
                    sub_note = random.choice(scale_notes + [bass_note + 7, bass_note + 12]) # Varia a nota
                    sub_velocity = random.randint(base_velocity - velocity_range - 20, base_velocity - velocity_range) # Mais suave

                    events.append(('note_on', sub_note, sub_velocity, current_sub_tick))
                    events.append(('note_off', sub_note, 0, current_sub_tick + sub_note_duration - (quantization_unit // 2)))
                    current_sub_tick += sub_note_duration
                else:
                    # Se não gerou nota, avança um pouco para dar espaço
                    current_sub_tick += quantization_unit
                
                # Garante que não ultrapasse o final da batida
                if current_sub_tick >= beat_start_tick + self.ticks_per_beat:
                    break
            
            current_tick = beat_start_tick + self.ticks_per_beat # Avança para a próxima batida

        return events

    def generate_chords(self, num_beats, progression_midi_notes):
        events = []
        
        current_tick = 0
        chord_duration = self.ticks_per_beat * 4 # Duração do acorde em compasso (4 batidas)

        progression_length = len(progression_midi_notes)
        
        for measure_num in range(num_beats // 4): # Para cada compasso
            # Seleciona o acorde da progressão (looping)
            chord_midi_notes = progression_midi_notes[measure_num % progression_length]
            
            # Toca o acorde no início do compasso
            for note in chord_midi_notes:
                # Ajusta a oitava do acorde, mantendo a tônica como referência, mas garantindo que as notas não fiquem muito baixas
                adjusted_note = note
                while adjusted_note < 48: # Garante que as notas não fiquem abaixo de C3
                    adjusted_note += 12

                velocity = random.randint(70, 90) # Variação de velocity
                events.append(('note_on', adjusted_note, velocity, current_tick))
                events.append(('note_off', adjusted_note, 0, current_tick + chord_duration - (self.ticks_per_beat // 16))) # Pequeno release
            
            current_tick += chord_duration # Avança para o próximo compasso

        return events

    def generate_lead_melody(self, root_key_str, scale_intervals, num_beats):
        events = []
        root_midi = self.root_notes[root_key_str]
        # Oitava mais alta para melodia, garantindo que a nota esteja em uma faixa MIDI válida
        scale_notes = [root_midi + interval + 24 for interval in scale_intervals if (root_midi + interval + 24) <= 96]
        
        current_tick = 0
        # Definir uma resolução de quantização para a melodia (ex: semicolcheia)
        quantization_unit = self.ticks_per_beat // 4 # Semicolcheia (120 ticks)

        # Reintroduzir mais variedade na melodia
        for beat_num in range(num_beats): # Loop para cada batida (quarter note)
            beat_start_tick = beat_num * self.ticks_per_beat
            
            # Decide quantas notas na melodia para esta batida (mais variação)
            num_notes_in_beat = random.randint(0, 4) # Pode ter de 0 a 4 notas por batida
            
            if num_notes_in_beat == 0 and random.random() < 0.3: # Pequena chance de silêncio total na batida
                current_tick += self.ticks_per_beat
                continue

            for i in range(num_notes_in_beat):
                # Garante que a nota comece em um ponto quantizado dentro da batida
                note_start_tick = beat_start_tick + (i * quantization_unit) 
                
                # Escolhe uma nota da escala ou um salto melódico pequeno
                if random.random() < 0.7: # Maior chance de seguir a escala
                    melody_note = random.choice(scale_notes)
                else: # Pequena chance de um salto para criar interesse
                    melody_note = random.choice([scale_notes[0] + 12, scale_notes[0] - 12] + scale_notes)

                # Evita notas muito fora da faixa comum
                if melody_note < 60: melody_note = 60 # C4
                if melody_note > 96: melody_note = 96 # C7 (para ter mais espaço)

                velocity = random.randint(75, 100) # Variação de velocity
                
                # Duração da nota: colcheia, semicolcheia, ou semínima (quantizada)
                duration_multipliers = [1, 2, 4] # Semicolcheia, Colcheia, Semínima
                duration_ticks = random.choice(duration_multipliers) * quantization_unit
                
                # Garante que a nota não ultrapasse o final da batida
                if note_start_tick + duration_ticks > beat_start_tick + self.ticks_per_beat:
                    duration_ticks = (beat_start_tick + self.ticks_per_beat) - note_start_tick
                    duration_ticks = (duration_ticks // quantization_unit) * quantization_unit
                    if duration_ticks <= 0: continue # Evita notas com duração zero ou negativa

                events.append(('note_on', melody_note, velocity, note_start_tick))
                # Ajusta a duração para não sobrepor a próxima nota perfeitamente, dando um pequeno "release"
                events.append(('note_off', melody_note, 0, note_start_tick + duration_ticks - (quantization_unit // 2))) 
                
            current_tick = beat_start_tick + self.ticks_per_beat # Avança o tick para a próxima batida completa

        return events


    def generate_pads(self, num_beats, progression_midi_notes):
        events = []
        
        current_tick = 0
        pad_duration = self.ticks_per_beat * 8 # Pad dura 2 compassos (8 batidas)
        
        progression_length = len(progression_midi_notes)

        for block_num in range(num_beats // 8): # Para cada bloco de 2 compassos
            # Seleciona o acorde da progressão (looping)
            # Usamos `block_num * 2` porque cada bloco tem 2 compassos e a progressão é por compasso.
            chord_midi_notes = progression_midi_notes[(block_num * 2) % progression_length]

            # Toca o acorde no início do bloco
            for note in chord_midi_notes:
                # Ajusta a oitava do pad, geralmente 2 oitavas acima da tônica, garantindo notas não muito altas
                adjusted_note = note + 12
                while adjusted_note < 60: # Garante que as notas não fiquem abaixo de C4
                    adjusted_note += 12
                if adjusted_note > 96: adjusted_note -= 12 # Evita notas muito agudas

                velocity = random.randint(50, 70) # Pads são mais suaves
                events.append(('note_on', adjusted_note, velocity, current_tick))
                events.append(('note_off', adjusted_note, 0, current_tick + pad_duration - (self.ticks_per_beat // 16))) # Pequeno release
            
            current_tick += pad_duration # Avança para o próximo bloco de 2 compassos

        return events

    def generate_arpeggio(self, num_beats, progression_midi_notes):
        events = []
        
        # Define a menor duração para as notas do arpejo (Fusa - 32nd note)
        arpeggio_quantization_options = [
            self.ticks_per_beat // 4,  # Semicolcheia (1/16)
            self.ticks_per_beat // 8,  # Fusa (1/32)
            self.ticks_per_beat // 16  # Semifusa (1/64)
        ]
        
        progression_length = len(progression_midi_notes)
        
        arpeggio_styles = ['up', 'down', 'up_down', 'random_order', 'broken_chord']

        for beat_num in range(num_beats): # Loop para cada batida
            current_beat_start_tick = beat_num * self.ticks_per_beat
            
            chord_midi_notes = progression_midi_notes[(beat_num // 4) % progression_length]
            
            # Estende as notas do acorde para incluir mais oitavas para o arpejo
            extended_arpeggio_notes = []
            for note in chord_midi_notes:
                if note - 24 >= 36: extended_arpeggio_notes.append(note - 24) # Duas oitavas abaixo
                if note - 12 >= 36: extended_arpeggio_notes.append(note - 12) # Oitava abaixo
                extended_arpeggio_notes.append(note)
                if note + 12 <= 108: extended_arpeggio_notes.append(note + 12) # Oitava acima
                if note + 24 <= 108: extended_arpeggio_notes.append(note + 24) # Duas oitavas acima
            extended_arpeggio_notes = sorted(list(set(extended_arpeggio_notes))) # Remove duplicatas e ordena
            
            # Filtra para uma faixa de oitavas mais razoável para arpejos (ex: C3 a C6)
            extended_arpeggio_notes = [n for n in extended_arpeggio_notes if 48 <= n <= 84] # C3 a C6

            # Escolhe um estilo de arpejo aleatoriamente para esta batida/bloco
            chosen_style = random.choice(arpeggio_styles)
            arpeggio_note_duration = random.choice(arpeggio_quantization_options) # Varia a duração

            arpeggio_pattern_notes = []
            if chosen_style == 'up':
                arpeggio_pattern_notes = extended_arpeggio_notes
            elif chosen_style == 'down':
                arpeggio_pattern_notes = list(reversed(extended_arpeggio_notes))
            elif chosen_style == 'up_down':
                # Garante que há notas suficientes para o padrão up_down
                if len(extended_arpeggio_notes) > 1:
                    arpeggio_pattern_notes = extended_arpeggio_notes + list(reversed(extended_arpeggio_notes[1:-1]))
                else: # Fallback se poucas notas
                    arpeggio_pattern_notes = extended_arpeggio_notes
            elif chosen_style == 'random_order':
                arpeggio_pattern_notes = random.sample(extended_arpeggio_notes, len(extended_arpeggio_notes))
            elif chosen_style == 'broken_chord': 
                # Escolhe 2-4 notas aleatórias do acorde original (não estendido) para formar o "broken"
                notes_from_chord_base = sorted([n for n in chord_midi_notes if 48 <= n <= 84]) # Filtrar para a oitava
                if notes_from_chord_base:
                    num_broken_notes = random.randint(2, min(4, len(notes_from_chord_base)))
                    arpeggio_pattern_notes = random.sample(notes_from_chord_base, num_broken_notes)
                    # Adiciona uma chance de variação de oitava para as notas do broken chord
                    arpeggio_pattern_notes = [n + random.choice([-12, 0, 12]) for n in arpeggio_pattern_notes]
                    arpeggio_pattern_notes = sorted([n for n in arpeggio_pattern_notes if 48 <= n <= 84]) # Re-filtrar faixa
                else: # Fallback se não houver notas no acorde original na faixa
                    arpeggio_pattern_notes = extended_arpeggio_notes
            
            if not arpeggio_pattern_notes: # Fallback final se o padrão estiver vazio por algum motivo
                arpeggio_pattern_notes = [60, 64, 67] # C Maj Triad

            # Garante que o arpejo preenche a batida com a duração escolhida
            notes_per_beat = self.ticks_per_beat // arpeggio_note_duration
            
            for i in range(notes_per_beat):
                arpeggio_note = arpeggio_pattern_notes[i % len(arpeggio_pattern_notes)]
                
                velocity = random.randint(65, 85) # Variação de velocity

                tick_position = current_beat_start_tick + (i * arpeggio_note_duration)
                
                events.append(('note_on', arpeggio_note, velocity, tick_position))
                events.append(('note_off', arpeggio_note, 0, tick_position + arpeggio_note_duration - (self.ticks_per_beat // 64))) # Pequeno release
        
        return events

    def generate_drums(self, num_beats):
        events = []
        # Definir notas MIDI para bateria (General MIDI Standard)
        KICK = 36  # C1
        SNARE = 38 # D1
        CLOSED_HIHAT = 42 # F#1
        OPEN_HIHAT = 46 # A#1
        RIDE = 51 # D#2
        CRASH = 49 # C#2

        # Velocities para groove
        kick_vel_strong = 105
        kick_vel_normal = 90
        kick_vel_ghost = 60 # Velocidade para kicks fantasmas/mais suaves
        snare_vel_strong = 100
        snare_vel_normal = 85
        hihat_vel_strong = 80
        hihat_vel_normal = 70
        hihat_vel_ghost = 60
        cymbal_vel = 110

        # Duração das notas de bateria (muito curtas)
        drum_note_duration = self.ticks_per_beat // 16 # Duração de 1/16 de nota (30 ticks)

        for beat_num in range(num_beats):
            current_beat_start_tick = beat_num * self.ticks_per_beat

            # --- Kick Drum ---
            # Kick no tempo (batidas 1 e 3 são mais fortes)
            kick_on_beat_velocity = kick_vel_strong if beat_num % 2 == 0 else kick_vel_normal
            events.append(('note_on', KICK, kick_on_beat_velocity, current_beat_start_tick))
            events.append(('note_off', KICK, 0, current_beat_start_tick + drum_note_duration))

            # Chance de kicks extras em semicolcheias para groove (mais variedade)
            if random.random() < 0.3: # 30% de chance de um kick extra na 2ª semicolcheia
                extra_kick_tick = current_beat_start_tick + (self.ticks_per_beat // 4)
                events.append(('note_on', KICK, kick_vel_ghost, extra_kick_tick))
                events.append(('note_off', KICK, 0, extra_kick_tick + drum_note_duration))
            
            if random.random() < 0.2 and beat_num % 2 == 1: # 20% de chance de um kick extra na 4ª semicolheia do beat 2 ou 4
                extra_kick_tick = current_beat_start_tick + (self.ticks_per_beat // 4) * 3
                events.append(('note_on', KICK, kick_vel_ghost, extra_kick_tick))
                events.append(('note_off', KICK, 0, extra_kick_tick + drum_note_duration))
            
            # --- Snare Drum ---
            # Snare no contra-tempo (batidas 2 e 4)
            snare_tick = current_beat_start_tick + (self.ticks_per_beat // 2) # Meio da batida
            snare_on_beat_velocity = snare_vel_strong 

            events.append(('note_on', SNARE, snare_on_beat_velocity, snare_tick))
            events.append(('note_off', SNARE, 0, snare_tick + drum_note_duration))

            # --- Hi-Hats (Semicolcheias consistentes com variação) ---
            for i in range(4): # 4 semicolheias por batida
                hihat_tick = current_beat_start_tick + (i * (self.ticks_per_beat // 4)) # Cada semicolheia
                
                hihat_velocity = hihat_vel_normal
                if i % 2 == 0: # 1ª e 3ª semicolheia (mais forte)
                    hihat_velocity = hihat_vel_strong
                else: # 2ª e 4ª semicolheia (mais suave)
                    hihat_velocity = hihat_vel_normal
                
                # Chance de hi-hat aberto no off-beat (geralmente na 2ª ou 4ª semicolheia)
                if i == 1 and random.random() < 0.3: # Pequena chance no 2º 16th (depois do beat)
                    events.append(('note_on', OPEN_HIHAT, hihat_velocity, hihat_tick))
                    events.append(('note_off', OPEN_HIHAT, 0, hihat_tick + drum_note_duration * 2)) # Dura mais
                elif i == 3 and random.random() < 0.5: # Maior chance no 4º 16th (antes do próximo beat)
                     events.append(('note_on', OPEN_HIHAT, hihat_velocity, hihat_tick))
                     events.append(('note_off', OPEN_HIHAT, 0, hihat_tick + drum_note_duration * 2)) # Dura mais
                else:
                    events.append(('note_on', CLOSED_HIHAT, hihat_velocity, hihat_tick))
                    events.append(('note_off', CLOSED_HIHAT, 0, hihat_tick + drum_note_duration))
            
            # --- Crash e Ride (mais esparsos) ---
            if beat_num == 0: # Crash no início do primeiro compasso
                events.append(('note_on', CRASH, cymbal_vel, current_beat_start_tick))
                events.append(('note_off', CRASH, 0, current_beat_start_tick + self.ticks_per_beat * 2)) # Dura 2 batidas

            if (beat_num + 1) % 4 == 0 and random.random() < 0.4: # Ride no final de cada 4 compassos (ou a cada 4 batidas)
                ride_tick = current_beat_start_tick + self.ticks_per_beat * 3 # No 4º beat
                events.append(('note_on', RIDE, cymbal_vel - 20, ride_tick))
                events.append(('note_off', RIDE, 0, ride_tick + self.ticks_per_beat)) # Dura 1 batida


        return events

    def save_midi_file(self, all_midi_events, filename, bpm):
        mid = mido.MidiFile(ticks_per_beat=self.ticks_per_beat)
        mid.tempo = mido.bpm2tempo(bpm) # Define o tempo principal do arquivo MIDI

        # Mapeamento de canais e nomes de partes
        part_channel_map = {
            'bass': {'channel': 0, 'program': 33},
            'chords': {'channel': 1, 'program': 1},
            'lead': {'channel': 2, 'program': 81},
            'pads': {'channel': 3, 'program': 89},
            'arpeggio': {'channel': 4, 'program': 81},
            'drums': {'channel': 9, 'program': 0}
        }

        # Cria uma trilha para cada parte gerada
        for part_name, part_data in part_channel_map.items():
            if part_name in all_midi_events:
                track = mido.MidiTrack()
                mid.tracks.append(track)
                
                # Define o programa (instrumento) para a trilha
                track.append(mido.Message('program_change', program=part_data['program'], channel=part_data['channel'], time=0))

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

        # Se não houver eventos, criar uma trilha vazia para o arquivo ser válido
        if not mid.tracks:
            mid.tracks.append(mido.MidiTrack())

        mid.save(filename)