// Test imageLoader function
function imageLoader({ src, width, quality }) {
    // If the image is from /media/, serve it directly without optimization
    if (src.startsWith('/media/')) {
        return src;
    }

    // If it's a full URL from our domain with /media/, extract the path
    if (src.includes('/media/')) {
        try {
            const url = new URL(src);
            if (url.hostname === 'peykantravelistanbul.com' ||
                url.hostname === 'www.peykantravelistanbul.com' ||
                url.hostname === 'localhost') {
                return url.pathname; // Return just the path part
            }
        } catch (e) {
            // If URL parsing fails, continue
            console.error('URL parsing failed:', e);
        }
    }

    // If it's an external URL, return as is
    if (src.startsWith('http://') || src.startsWith('https://')) {
        return src;
    }

    // For other images, use default Next.js optimization
    return `/_next/image?url=${encodeURIComponent(src)}&w=${width}&q=${quality || 75}`;
}

// Test cases
const testCases = [
    '/media/products/image.jpg',
    'https://peykantravelistanbul.com/media/products/tours-istanbul-new-NewFolder-_IvhkcM3.jpg',
    'https://www.peykantravelistanbul.com/media/products/image.jpg',
    'https://external.com/image.jpg',
    '/images/local.jpg'
];

console.log('Testing imageLoader:');
testCases.forEach(src => {
    const result = imageLoader({ src, width: 1920, quality: 85 });
    console.log(`Input:  ${src}`);
    console.log(`Output: ${result}`);
    console.log('---');
});
