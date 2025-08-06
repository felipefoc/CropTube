# CropTube

CropTube is a web application that allows you to download and trim YouTube videos. Simply paste a YouTube URL, select your desired quality and format, and use the sliders to trim the video to your liking.

## Features

*   **Download YouTube Videos:** Download videos from YouTube by pasting the URL.
*   **Select Quality and Format:** Choose from various video qualities and formats (MP4, AVI, MP3).
*   **Trim Videos:** Use the intuitive sliders to select the start and end times of the video.
*   **Live Preview:** See a live preview of the YouTube video.
*   **Download Trimmed Video:** Download the final trimmed video to your device.

## Technologies Used

*   **Backend:** Python, Flask
*   **Frontend:** HTML, CSS, JavaScript
*   **Video Processing:** yt-dlp, FFmpeg
*   **Containerization:** Docker, Docker Compose

## Getting Started

### Prerequisites

*   Docker
*   Docker Compose

### Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/your-username/croptube.git
    cd croptube
    ```

2.  **Run with Docker Compose:**

    ```bash
    docker-compose up
    ```

3.  **Access the application:**

    Open your web browser and navigate to `http://localhost:5000`.

## How to Use

1.  **Paste the YouTube URL:** Paste the URL of the YouTube video you want to download and trim into the input field.
2.  **Select Format and Quality:** Choose your desired format (MP4, AVI, or MP3) and video quality from the dropdown menus.
3.  **Trim the Video:** Use the sliders to select the start and end times for your video.
4.  **Download:** Click the "Recortar" (Trim) button to process and download your video.
