export default function imageLoader({ src, width, quality }) {
    // If the image is from /media/ or /images/, serve it directly without optimization
    if (src.startsWith('/media/') || src.startsWith('/images/')) {
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
        }
    }

    // If it's an external URL, return as is
    if (src.startsWith('http://') || src.startsWith('https://')) {
        return src;
    }

    // For other images, use default Next.js optimization
    return `/_next/image?url=${encodeURIComponent(src)}&w=${width}&q=${quality || 75}`;
}
