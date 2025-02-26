export class PhotoManager {
    constructor() {
        this.currentPhoto = document.getElementById('current-photo');
        this.photoView = document.getElementById('photo-container');
        this.calendarView = document.querySelector('.container');
        this.header = document.querySelector('.header');
        this.body = document.querySelector('body');
        this.photos = [];
        this.shuffledPhotos = [];
        this.currentIndex = 0;
        this.defaultPhoto = "/static/photo.jpg";
    }

    async initialize() {
        try {
            this.photos = await fetch('/get_photos').then(res => res.json());
            if (!Array.isArray(this.photos) || this.photos.length === 0) {
                console.warn("No photos available, using default image.");
                this.photos = [this.defaultPhoto];
            }
            this.shufflePhotos();
        } catch (error) {
            console.error("Error fetching photos:", error);
            this.photos = [this.defaultPhoto];
        }
    }

    shufflePhotos() {
        // Create a copy of the photos array
        this.shuffledPhotos = [...this.photos];

        // Fisher-Yates shuffle algorithm
        for (let i = this.shuffledPhotos.length - 1; i > 0; i--) {
            const j = Math.floor(Math.random() * (i + 1));
            [this.shuffledPhotos[i], this.shuffledPhotos[j]] =
            [this.shuffledPhotos[j], this.shuffledPhotos[i]];
        }

        this.currentIndex = 0;
    }

    getNextPhoto() {
        // If we've shown all photos, reshuffle
        if (this.currentIndex >= this.shuffledPhotos.length) {
            this.shufflePhotos();
        }

        return this.shuffledPhotos[this.currentIndex++];
    }

    preloadNewPhoto() {
        const newPhoto = new Image();
        newPhoto.src = this.getNextPhoto();
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