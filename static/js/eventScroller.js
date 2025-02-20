export class EventScroller {
    constructor() {
        this.SCROLL_SPEED = 0.5;
        this.SCROLL_INTERVAL = 16;
        this.PAUSE_DURATION = 3000;
        this.scrollableContainers = [];
        this.isScrolling = true;
        this.isPaused = false;
        this.pauseTimeout = null;
        this.scrollInterval = null;
    }

    initialize() {
        const dayCards = document.querySelectorAll('.day-card');
        this.setupContainers(dayCards);
        if (this.scrollableContainers.length > 0) {
            this.startScrolling();
        }
    }

    setupContainers(dayCards) {
        dayCards.forEach(card => {
            const events = card.querySelectorAll('.event');
            if (events.length === 0) return;

            const { eventsWrapper, scrollContainer } = this.createScrollContainer();
            this.moveEventsToContainer(events, scrollContainer);
            card.querySelector('.day-header').after(eventsWrapper);

            const totalHeight = this.calculateTotalHeight(events);
            if (totalHeight > eventsWrapper.clientHeight) {
                this.scrollableContainers.push({
                    container: scrollContainer,
                    totalHeight: totalHeight,
                    wrapperHeight: eventsWrapper.clientHeight,
                    scrollPosition: 0,
                    maxScroll: totalHeight - eventsWrapper.clientHeight
                });
            }
        });
    }

    createScrollContainer() {
        const eventsWrapper = document.createElement('div');
        eventsWrapper.className = 'events-container';
        const scrollContainer = document.createElement('div');
        scrollContainer.className = 'events-scroll';
        eventsWrapper.appendChild(scrollContainer);
        return { eventsWrapper, scrollContainer };
    }

    moveEventsToContainer(events, scrollContainer) {
        events.forEach(event => {
            event.parentElement.removeChild(event);
            scrollContainer.appendChild(event);
        });
    }

    calculateTotalHeight(events) {
        return Array.from(events).reduce((total, event) =>
            total + event.offsetHeight +
            parseInt(getComputedStyle(event).marginTop) +
            parseInt(getComputedStyle(event).marginBottom), 0);
    }

    startScrolling() {
        const maxScrollDistance = Math.max(...this.scrollableContainers.map(container => container.maxScroll));
        this.scrollInterval = setInterval(() => this.scrollAll(maxScrollDistance), this.SCROLL_INTERVAL);
    }

    scrollAll(maxScrollDistance) {
        if (!window.showingCalendar || !this.isScrolling || this.isPaused) return;

        let maxCurrentScroll = 0;
        this.scrollableContainers.forEach(scrollData => {
            scrollData.scrollPosition += this.SCROLL_SPEED;
            if (scrollData.scrollPosition > scrollData.maxScroll) {
                scrollData.scrollPosition = scrollData.maxScroll;
            }
            maxCurrentScroll = Math.max(maxCurrentScroll, scrollData.scrollPosition);
            scrollData.container.style.transform = `translateY(-${scrollData.scrollPosition}px)`;
        });

        if (maxCurrentScroll >= maxScrollDistance) {
            this.pauseScrolling();
        }
    }

    pauseScrolling() {
        this.isPaused = true;
        if (this.pauseTimeout) clearTimeout(this.pauseTimeout);
        this.pauseTimeout = setTimeout(() => {
            this.resetAllScrolls();
            setTimeout(() => {
                this.isScrolling = true;
                this.isPaused = false;
            }, 100);
        }, this.PAUSE_DURATION);
    }

    resetAllScrolls() {
        this.scrollableContainers.forEach(scrollData => {
            scrollData.scrollPosition = 0;
            scrollData.container.style.transform = `translateY(0)`;
        });
    }

    cleanup() {
        if (this.scrollInterval) clearInterval(this.scrollInterval);
        if (this.pauseTimeout) clearTimeout(this.pauseTimeout);
    }
}