document.addEventListener('DOMContentLoaded', function() {
    const container = document.querySelector('.container'); // Target the container div
    const totalHeight = container.scrollHeight; // Get the total scrollable height of the container
    const viewportHeight = container.clientHeight; // Get the height of the visible area of the container
    const duration = 10000; // Total duration of each scroll up or down in milliseconds
    let isScrollingDown = true; // Flag to track scroll direction

    function scrollContent() {
        const startTime = performance.now();

        function scrollStep(currentTime) {
            const elapsedTime = currentTime - startTime;
            const progress = Math.min(elapsedTime / duration, 1); // Calculate the scroll progress

            if (isScrollingDown) {
                // Scroll down
                const scrollPosition = progress * (totalHeight - viewportHeight);
                container.scrollTo(0, scrollPosition);
            } else {
                // Scroll up
                const scrollPosition = (1 - progress) * (totalHeight - viewportHeight);
                container.scrollTo(0, scrollPosition);
            }

            if (progress < 1) {
                requestAnimationFrame(scrollStep);
            } else {
                // After finishing the scroll, reverse the direction and repeat
                isScrollingDown = !isScrollingDown;
                setTimeout(scrollContent, 1000); // Wait 1 second before reversing the scroll direction
            }
        }

        requestAnimationFrame(scrollStep);
    }

    scrollContent(); // Start the scroll when the page loads
});
