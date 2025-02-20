export class PhotoManager {
    constructor() {
        this.currentPhoto = document.getElementById('current-photo');
        this.photoView = document.getElementById('photo-container');
        this.calendarView = document.querySelector('.container');
        this.header = document.querySelector('.header');
        this.body = document.querySelector('body');
        this.photos = [];
        this.lastShownIndex = -1;
        this.defaultPhoto = "/static/photo.jpg";
    }

    async initialize() {
        try {
            this.photos = await fetch('/get_photos').then(res => res.json());
            if (!Array.isArray(this.photos) || this.photos.length === 0) {
                console.warn("No photos available, using default image.");
                this.photos = [this.defaultPhoto];
            }
        } catch (error) {
            console.error("Error fetching photos:", error);
            this.photos = [this.defaultPhoto];
        }
    }

    getRandomPhoto() {
        let newIndex;
        do {
            newIndex = Math.floor(Math.random() * this.photos.length);
        } while (newIndex === this.lastShownIndex && this.photos.length > 1);
        this.lastShownIndex = newIndex;
        return this.photos[newIndex];
    }

    preloadNewPhoto() {
        const newPhoto = new Image();
        newPhoto.src = this.getRandomPhoto();
        newPhoto.style.position = 'absolute';
        newPhoto.style.top = '0';
        newPhoto.style.left = '0';
        newPhoto.style.width = '100%';
        newPhoto.style.height = '100%';
        newPhoto.style.objectFit = 'cover';
        newPhoto.style.transition = 'opacity 1s ease-in-out';
        newPhoto.style.opacity = 0;

        this.photoView.appendChild(newPhoto);

        newPhoto.onload = () => {
            newPhoto.style.opacity = 1;
            if (this.currentPhoto) {
                this.currentPhoto.style.transition = 'opacity 1s ease-in-out';
                this.currentPhoto.style.opacity = 0;
                setTimeout(() => {
                    if (this.currentPhoto.parentNode) {
                        this.currentPhoto.parentNode.removeChild(this.currentPhoto);
                    }
                    this.currentPhoto = newPhoto;
                }, 1000);
            } else {
                this.currentPhoto = newPhoto;
            }
        };
    }
}