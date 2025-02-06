document.addEventListener('DOMContentLoaded', async () => {
    const CALENDAR_INTERVAL = 30000; // Time between calendar/photo switches
    const PHOTO_INTERVAL = CALENDAR_INTERVAL / 5; // Time between photo changes
    const FIRST_PHOTO_DELAY = 3000; // Delay for the first photo to stay on screen

    const calendarView = document.querySelector('.container');
    const photoView = document.getElementById('photo-container');
    const currentPhoto = document.getElementById('current-photo');
    const body = document.querySelector('body');  // Select the body for background color

    let photos = [];
    let lastShownIndex = -1;
    let showingCalendar = true;
    const defaultPhoto = "/static/default.jpg"; // Fallback if no photos exist

    try {
        photos = await fetch('/get_photos').then(res => res.json());
        if (!Array.isArray(photos) || photos.length === 0) {
            console.warn("No photos available, using default image.");
            photos = [defaultPhoto];
        }
    } catch (error) {
        console.error("Error fetching photos:", error);
        photos = [defaultPhoto]; // Ensure there's at least one image
    }

    function getRandomPhoto() {
        let newIndex;
        do {
            newIndex = Math.floor(Math.random() * photos.length);
        } while (newIndex === lastShownIndex && photos.length > 1);
        lastShownIndex = newIndex;
        return photos[newIndex];
    }

    function toggleView() {
        if (showingCalendar) {
            // Hide calendar, show photo
            calendarView.classList.add('hide-calendar');
            photoView.classList.add('show-photo');
            currentPhoto.src = getRandomPhoto();
            body.style.backgroundColor = 'black'; // Set background to black when showing photo
            body.style.setProperty('--bg-image', 'none'); // Hide background image during photo view
        } else {
            // Show calendar, hide photo
            calendarView.classList.remove('hide-calendar');
            photoView.classList.remove('show-photo');
            body.style.backgroundColor = ''; // Reset background to default when showing calendar
            body.style.setProperty('--bg-image', 'url("/static/photo.jpg")'); // Restore background image when showing calendar
        }
        showingCalendar = !showingCalendar;
    }

    function fadeInPhoto() {
        currentPhoto.style.opacity = 0;
        setTimeout(() => {
            currentPhoto.src = getRandomPhoto();
            currentPhoto.style.transition = 'opacity 1s ease-in-out';
            currentPhoto.style.opacity = 1;
        }, 500); // Wait for half a second before changing the photo
    }

    // Delay the first transition to allow the first photo to stay
    setTimeout(() => {
        toggleView();  // Trigger the first photo switch
    }, FIRST_PHOTO_DELAY);

    // Regular interval for switching between calendar and photo
    setInterval(() => {
        toggleView();
    }, CALENDAR_INTERVAL);

    // Regular interval for updating the photo without toggling the view
    setInterval(() => {
        if (!showingCalendar) {
            fadeInPhoto();  // Use fade-in effect for photo transitions
        }
    }, PHOTO_INTERVAL);
});
