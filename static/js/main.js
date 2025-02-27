import { PhotoManager } from './photoManager.js';
import { EventScroller } from './eventScroller.js';

document.addEventListener('DOMContentLoaded', async () => {
    document.body.classList.add('cursor-hidden');

    let cursorTimeout;
    document.addEventListener('mousemove', () => {
        document.body.classList.remove('cursor-hidden');
        clearTimeout(cursorTimeout);
        cursorTimeout = setTimeout(() => {
            document.body.classList.add('cursor-hidden');
        }, 3000);  // Hide cursor after 3 seconds of inactivity
    });

    // Get intervals from server config
    const config = await fetch('/config').then(res => res.json());
    const CALENDAR_INTERVAL = config.CALENDAR_INTERVAL;
    const PHOTO_INTERVAL = config.PHOTO_INTERVAL;
    const TRANSITION_DELAY = 1000; // Delay for the first photo to stay on screen

    window.showingCalendar = true;
    const photoManager = new PhotoManager();
    const eventScroller = new EventScroller();

    await photoManager.initialize();
    eventScroller.initialize();

    function toggleView() {
        if (window.showingCalendar) {
            // Hide calendar, show photo
            photoManager.photoView.style.transition = 'opacity 1s ease-in-out';
            photoManager.photoView.style.opacity = 1;
            setTimeout(() => {
                photoManager.calendarView.classList.add('hide-calendar');
                photoManager.body.style.setProperty('--bg-image', 'none'); // Hide background image during photo view
                photoManager.body.style.backgroundColor = 'rgba(0, 0, 0, 1)';  // Set background color to full opacity
                photoManager.header.classList.add('hidden');
                eventScroller.setVisibility(false); // Stop scrolling when calendar is hidden
            }, TRANSITION_DELAY); // Wait 1 second (1000 milliseconds) before executing the code
        } else {
            // Show calendar, hide photo
            photoManager.header.classList.remove('hidden');
            photoManager.body.style.backgroundColor = 'rgba(0, 0, 0, 0.5)';  // Set background color with opacity
            photoManager.calendarView.classList.remove('hide-calendar');
            photoManager.body.style.setProperty('--bg-image', 'url("/static/photo.jpg")'); // Restore background image when showing calendar
            eventScroller.setVisibility(true); // Resume scrolling when calendar is shown
            setTimeout(() => {
                photoManager.photoView.style.transition = 'opacity 1s ease-in-out';
                photoManager.photoView.style.opacity = 0;
            }, TRANSITION_DELAY);
        }
        window.showingCalendar = !window.showingCalendar;
    }

    // Regular interval for switching between calendar and photo
    setInterval(toggleView, CALENDAR_INTERVAL);

    // Regular interval for updating the photo without toggling the view
    setInterval(() => {
        if (!window.showingCalendar) {
            photoManager.preloadNewPhoto();  // Preload and fade the current photo
        }
    }, PHOTO_INTERVAL);

    window.addEventListener('beforeunload', () => {
        eventScroller.cleanup();
    });
});
