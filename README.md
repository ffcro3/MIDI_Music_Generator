# MIDI Music Generator

## 🎶 Unleash Your Inner Liquid Funk Producer! 🚀

Welcome to the **MIDI Funk Music Generator**, a desktop application designed to spark your creativity and accelerate your music production workflow. Ever wanted to quickly sketch out a full Liquid Funk track, complete with groovy basslines, ethereal pads, melodic leads, and tight drums? This tool is your answer!

Built with Python and `tkinter` for the GUI, `mido` for MIDI manipulation, and `pygame` for real-time playback, this generator allows you to create MIDI compositions with customizable parameters and instantly hear your ideas come to life. Whether you're a seasoned producer looking for fresh inspiration or a beginner eager to explore music theory in action, this project is built for you.

### Why This Project Exists

In the fast-paced world of music production, inspiration can strike at any moment, but the technicalities of laying down a full track can often slow down the creative flow. This generator aims to bridge that gap by:

* **Accelerating Idea Generation:** Quickly generate full-fledged musical ideas based on your chosen key, scale, and BPM.

* **Demystifying Music Theory:** Observe how different musical parts (bass, chords, lead, etc.) interact within a harmonious structure.

* **Empowering Experimentation:** Easily tweak parameters and regenerate, exploring countless musical possibilities without deep manual effort.

* **Providing a Foundation:** Generate MIDI files ready for further refinement, arrangement, and mixing in your Digital Audio Workstation (DAW).

We believe that creativity should be boundless, and tools like this can help unlock new avenues for musical exploration.

## ✨ Features

* **Intuitive GUI:** A clean and user-friendly interface built with `tkinter`.

* **Customizable Parameters:** Adjust BPM, duration, root key, and scale type to fit your desired mood.

* **Part-Based Generation:** Independently enable/disable generation for Bass, Chords, Lead, Pads, Arpeggio, and Drums.

* **Real-time MIDI Playback:** Listen to your generated music instantly within the application using `pygame.mixer`.

* **Integrated MIDI Visualizer:** See the generated MIDI notes in real-time, providing a visual representation of your composition.

* **Organized Project Saving:**

  * **Project Name Input:** Define a custom name for your musical project.

  * **Dedicated Project Folders:** All generated MIDI files for a project are saved into a dedicated folder (`MIDIs_Gerados/YourProjectName`).

  * **Timestamped Files:** Each generated MIDI file (full mix or individual parts) includes a timestamp in its filename, ensuring unique versions and easy tracking of your iterations.

  * **Separated Parts Folders:** Within your project folder, individual parts (e.g., `Bass/`, `Lead/`) are stored in their own subdirectories for optimal organization.

* **One-Click Folder Access:** Easily open the generated MIDI project folder directly from the application.

## 🚀 Getting Started

Follow these steps to get the Liquid Funk Music Generator up and running on your machine.

### Prerequisites

Before you begin, ensure you have Python 3.8+ installed on your system.

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/ffcro3/MIDI_Music_Generator.git
    cd MIDI_Music_Generator
    ```

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    ```

3.  **Activate the virtual environment:**
    * **macOS / Linux:**
        ```bash
        source venv/bin/activate
        ```
    * **Windows:**
        ```bash
        .\venv\Scripts\activate
        ```

4.  **Install the required dependencies:**
    ```bash
    pip install mido pygame
    ```

### How to Run

After installation, simply run the main application file:

```bash
python app_gui.py
```

## 💻 How to Use

1.  **Set Project Name:** Enter a descriptive name for your musical project in the "Project Name" field. This will be the name of the main folder where your MIDIs will be saved.

2.  **Set a Genre:** Drum and bass, House, Trance and Pystrance (evaualing new genres) 

3.  **Adjust Parameters:**

    * **BPM:** Set the tempo (e.g., 174 for classic Liquid Funk).

    * **Duration (Measures):** Define the length of your composition in 4/4 measures.

    * **Root Key:** Choose the tonic (e.g., 'A', 'C#').

    * **Scale Type:** Select between 'Major' or 'Minor' scales.

4.  **Select Parts:** Check the boxes for the musical parts you wish to generate (Bass, Chords, Lead, Pads, Arpeggio, Drums).

5.  **Generate MIDI:** Click the **`Gerar MIDI`** (Generate MIDI) button. The application will compute the musical parts and display them in the visualizer. A temporary MIDI file is created for immediate playback.

6.  **Reproduce MIDI:** Click the **`Reproduzir MIDI`** (Play MIDI) button to listen to the generated track.

7.  **Stop Playback:** Click **`Parar Reprodução`** (Stop Playback) to halt the audio.

8.  **Save MIDI:**

    * Click the **`Salvar MIDI`** (Save MIDI) dropdown button.

    * Choose **`Salvar MIDI Completo...`** to save the full mixed track.

    * Choose **`Salvar Partes Separadas...`** to save each generated part into its own subfolder.

    * All files will be saved in `MIDIs_Gerados/YourProjectName/` with timestamps (e.g., `Full_Mix_20240530_143000.mid`, `bass_20240530_143000.mid`).

9.  **Open MIDI Folder:** Click **`Abrir Pasta de MIDIs Gerados`** (Open Generated MIDIs Folder) to directly access the project folder where your MIDI files are stored.

## 🤝 Contributing

We welcome contributions from the community! Whether you're a developer, a musician, or both, your insights and efforts can help shape the future of this project.

### How to Contribute

1.  **Fork the repository.**

2.  **Create a new branch** for your feature or bug fix: `git checkout -b feature/your-feature-name` or `bugfix/issue-description`.

3.  **Implement your changes.**

4.  **Write clear commit messages.**

5.  **Push your branch** to your forked repository.

6.  **Open a Pull Request** to the `main` branch of this repository, describing your changes in detail.

### Ideas for Contribution

* **New Musical Styles:** Implement generation logic for other genres (e.g., House, Techno, Trance).

* **Advanced Music Theory:** Add support for more complex scales, chords, or rhythm patterns.

* **UI/UX Improvements:** Enhance the user interface for even greater ease of use.

* **Export Options:** Add functionality to export to other audio formats (e.g., WAV, MP3) using external libraries (e.g., `fluidsynth`).

* **Performance Optimization:** Improve the speed of MIDI generation and playback.

* **Testing:** Write unit and integration tests to ensure robustness.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](https://opensource.org/licenses/MIT) file for details.

## 🌟 Show Your Support

If you find this project useful or interesting, please consider giving it a star ⭐️ on GitHub! Your support helps motivate further development and encourages new contributors.

## 📧 Contact

For any questions, suggestions, or collaborations, feel free to open an issue on GitHub or reach out to [https://www.linkedin.com/in/rochafabricio/].