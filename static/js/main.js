document.addEventListener('DOMContentLoaded', async () => {
    const CALENDAR_INTERVAL = 30000; // Time between calendar/photo switches
    const PHOTO_INTERVAL = CALENDAR_INTERVAL / 5; // Time between photo changes
    const TRANSITION_DELAY = 1000; // Delay for the first photo to stay on screen

    const calendarView = document.querySelector('.container');
    const photoView = document.getElementById('photo-container');
    const body = document.querySelector('body');  // Select the body for background color
    const header = document.querySelector('.header');

    let currentPhoto = document.getElementById('current-photo');
    let node = null;
    let photos = [];
    let lastShownIndex = -1;
    let showingCalendar = true;
    const defaultPhoto = "/static/photo.jpg"; // Fallback if no photos exist

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
            photoView.style.transition = 'opacity 1s ease-in-out';
            photoView.style.opacity = 1;
            setTimeout(() => {
                calendarView.classList.add('hide-calendar');
                body.style.setProperty('--bg-image', 'none'); // Hide background image during photo view
                body.style.backgroundColor = 'rgba(0, 0, 0, 1)';  // Set background color to full opacity
                header.classList.add('hidden');
            }, TRANSITION_DELAY); // Wait 1 second (1000 milliseconds) before executing the code
            //preloadNewPhoto();  // Preload and fade the current photo
        } else {
            // Show calendar, hide photo
            header.classList.remove('hidden');
            body.style.backgroundColor = 'rgba(0, 0, 0, 0.5)';  // Set background color with opacity
            calendarView.classList.remove('hide-calendar');
            body.style.setProperty('--bg-image', 'url("/static/photo.jpg")'); // Restore background image when showing calendar
            setTimeout(() => {
                photoView.style.transition = 'opacity 1s ease-in-out';
                photoView.style.opacity = 0;
            }, TRANSITION_DELAY);
        }
        showingCalendar = !showingCalendar;
    }

    function preloadNewPhoto() {
        // Create and preload a new image in the background
        const newPhoto = new Image();
        newPhoto.src = getRandomPhoto();
        newPhoto.style.position = 'absolute';
        newPhoto.style.top = '0';
        newPhoto.style.left = '0';
        newPhoto.style.width = '100%';
        newPhoto.style.height = '100%';
        newPhoto.style.objectFit = 'cover';
        newPhoto.style.transition = 'opacity 1s ease-in-out';
        newPhoto.style.opacity = 0;  // Start with 0 opacity

        // Append the new photo to the container, but behind the current photo
        photoView.appendChild(newPhoto);

        // Once the image is loaded, fade it in over the calendar
        newPhoto.onload = () => {
            // Fade in the new photo
            newPhoto.style.opacity = 1;

            // If there is a current photo, fade it out
            if (currentPhoto) {
                currentPhoto.style.transition = 'opacity 1s ease-in-out';
                currentPhoto.style.opacity = 0;  // Fade out the current photo

                // Wait for the current photo to fade out completely
                setTimeout(() => {
                    // Remove the old photo from the DOM if it exists
                    if (currentPhoto.parentNode) {
                        currentPhoto.parentNode.removeChild(currentPhoto);
                    }

                    // Update the currentPhoto reference to the new photo
                    currentPhoto = newPhoto;
                }, TRANSITION_DELAY); // 1 second for the fade-out effect
            } else {
                // If there's no current photo, just set the new photo as current
                currentPhoto = newPhoto;
            }
        };
    }




    // Regular interval for switching between calendar and photo
    setInterval(() => {
        toggleView();
    }, CALENDAR_INTERVAL);

    // Regular interval for updating the photo without toggling the view
    setInterval(() => {
        if (!showingCalendar) {
            preloadNewPhoto();  // Preload and fade the current photo
        }
    }, PHOTO_INTERVAL);
});
