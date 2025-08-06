let lastUrl = '';
let timeoutId = null;

// Utility function to show/hide elements
function toggleElements(url, isValidUrl) {
    const settingsContainer = document.querySelector('.settings-container');
    const qualitySelect = document.getElementById('quality');
    const formatSelect = document.getElementById('format');
    const previewContainer = document.getElementById('preview-container');

    if (url && isValidUrl) {
        settingsContainer.style.display = 'flex';
        previewContainer.style.display = 'block';

        if (formatSelect.value !== 'mp3') {
            qualitySelect.style.display = 'block';
        } else {
            qualitySelect.style.display = 'none';
        }
    } else {
        settingsContainer.style.display = 'none';
        qualitySelect.style.display = 'none';
        previewContainer.style.display = 'none';
    }
}

// Handle URL input with debouncing
document.getElementById('url').addEventListener('input', async (event) => {
    const url = event.target.value.trim();
    const videoId = getYouTubeVideoId(url);
    const isValidUrl = url && videoId;

    // Clear previous timeout
    if (timeoutId) {
        clearTimeout(timeoutId);
    }

    toggleElements(url, isValidUrl);

    if (url && isValidUrl && url !== lastUrl) {
        const qualitySelect = document.getElementById('quality');
        const previewFrame = document.getElementById('youtube-preview');
        buttonCrip = document.getElementById('submit');
        qualitySelect.innerHTML = '<option value="">Loading...</option>';

        // Update preview
        previewFrame.src = `https://www.youtube.com/embed/${videoId}?autoplay=1&mute=1`;

        // Set a timeout to fetch qualities and video info
        timeoutId = setTimeout(async () => {
            lastUrl = url;
            try {
                // Fetch qualities
                const qualitiesResponse = await fetch('/get-qualities', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ url })
                });

                // Fetch video info for duration
                const infoResponse = await fetch('/get_video_info', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ url })
                });

                if (qualitiesResponse.ok) {
                    const data = await qualitiesResponse.json();
                    // Update quality options
                    qualitySelect.innerHTML = '';
                    data.qualities.forEach(quality => {
                        const option = document.createElement('option');
                        option.value = quality.format_id;
                        option.textContent = quality.quality;
                        qualitySelect.appendChild(option);
                    });
                    buttonCrip.style.display = 'block';
                }

                if (infoResponse.ok) {
                    const info = await infoResponse.json();
                    if (info.duration) {
                        setupSliders(info.duration);
                    }
                }
            } catch (error) {
                console.error('Error fetching qualities:', error);
                qualitySelect.innerHTML = '<option value="">Error loading qualities</option>';
            }
        }, 500); // Wait 500ms after last input before fetching
    } else if (!url) {
        lastUrl = '';
        clearElements();
    }
});

function formatTime(seconds) {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.round(seconds % 60);
    return `${minutes}m ${remainingSeconds}s`;
}

function setupSliders(duration) {
    const slidersContainer = document.getElementById('sliders-container');
    const startSlider = document.getElementById('start-slider');
    const endSlider = document.getElementById('end-slider');
    const startTime = document.getElementById('start-time');
    const endTime = document.getElementById('end-time');

    startSlider.max = duration;
    startSlider.value = 0;
    endSlider.max = duration;
    endSlider.value = duration;

    startTime.textContent = formatTime(startSlider.value);
    endTime.textContent = formatTime(endSlider.value);

    startSlider.addEventListener('input', () => {
        startTime.textContent = formatTime(startSlider.value);
        if (parseInt(startSlider.value) > parseInt(endSlider.value)) {
            endSlider.value = startSlider.value;
            endTime.textContent = formatTime(endSlider.value);
        }
    });

    endSlider.addEventListener('input', () => {
        endTime.textContent = formatTime(endSlider.value);
        if (parseInt(endSlider.value) < parseInt(startSlider.value)) {
            startSlider.value = endSlider.value;
            startTime.textContent = formatTime(startSlider.value);
        }
    });

    slidersContainer.style.display = 'block';
}

// Handle format changes
document.getElementById('format').addEventListener('change', (event) => {
    const qualitySelect = document.getElementById('quality');
    const format = event.target.value;
    
    if (format === 'mp3') {
        qualitySelect.style.display = 'none';
    } else {
        // Only show quality if we have a valid URL
        const url = document.getElementById('url').value.trim();
        if (url && getYouTubeVideoId(url)) {
            qualitySelect.style.display = 'block';
        }
    }
});

document.getElementById('download-form').addEventListener('submit', async (event) => {
    event.preventDefault();

    const downloadButton = document.querySelector('#download-form button');
    const loadingIndicator = document.getElementById('loading-indicator');
    const playerContainer = document.getElementById('player-container');
    const downloadLink = document.getElementById('download-link');
    const previewContainer = document.getElementById('preview-container');

    downloadButton.disabled = true;
    loadingIndicator.style.display = 'block';
    playerContainer.style.display = 'none';
    downloadLink.style.display = 'none';
    previewContainer.style.display = 'none';

    const url = document.getElementById('url').value;
    const startTime = document.getElementById('start-slider').value;
    const endTime = document.getElementById('end-slider').value;
    const quality = document.getElementById('quality').value;
    const format = document.getElementById('format').value;

    try {
        const response = await fetch('/download', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ url, start_time: startTime, end_time: endTime, quality, format })
        });

        const data = await response.json();
        
        if (response.ok && data.filename) {
            const videoPath = '/static/videos/' + data.filename;
            const videoPlayer = document.getElementById('video-player');
            
            // Hide loading indicator and show download link
            loadingIndicator.style.display = 'none';
            playerContainer.style.display = 'block';
            downloadLink.href = videoPath;
            downloadLink.style.display = 'block';
            videoPlayer.src = videoPath;

            // Remove the preview container if it exists
            const previewContainer = document.getElementById('preview-container');
            if (previewContainer) {
                previewContainer.style.display = 'none';
            }
        } else {
            alert(data.error || 'An error occurred during download');
            loadingIndicator.style.display = 'none';
        }
    } finally {
        downloadButton.disabled = false;
    }
});

function getYouTubeVideoId(url) {
    const regex = /(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?|shorts)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})/; 
    const match = url.match(regex);
    return match ? match[1] : null;
}

// Clear elements when URL is empty
function clearElements() {
    const previewContainer = document.getElementById('preview-container');
    const settingsContainer = document.querySelector('.settings-container');
    const submitButton = document.querySelector('#download-form button');
    
    previewContainer.style.display = 'none';
    settingsContainer.style.display = 'none';
    submitButton.style.display = 'none';
}