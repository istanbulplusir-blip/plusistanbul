# 🔧 رفع مشکلات Hero Slider

## 🎯 خلاصه مشکلات شناسایی شده

بعد از بررسی دقیق کد بک‌اند و فرانت‌اند، مشکلات زیر شناسایی شد:

### 1. ⚠️ منطق has_video در فرانت‌اند

**مشکل**: 
```typescript
const hasVideo = currentSlideData?.has_video || currentHeroSlide?.has_video
```

این منطق فقط به فیلد `has_video` از API اعتماد می‌کند و خودش چک نمی‌کند.

**راه‌حل**:
```typescript
const hasVideo = currentSlideData && (
  (currentSlideData.video_type === 'file' && currentSlideData.video_file_url) ||
  (currentSlideData.video_type === 'url' && currentSlideData.video_url)
)
```

---

### 2. ⚠️ Fallback های نادرست

**مشکل**:
```typescript
const videoSrc = currentSlideData?.video_file_url || currentSlideData?.video_url || "/images/istanbul-heli.mp4"
```

فایل `/images/istanbul-heli.mp4` ممکن است وجود نداشته باشد.

**راه‌حل**:
```typescript
const videoSrc = currentSlideData?.video_file_url || currentSlideData?.video_url || ""
const videoPoster = currentSlideData?.video_thumbnail_url || 
                    currentHeroSlide?.desktop_image_url || 
                    siteSettings?.default_hero_image_url || 
                    "/images/hero-main.jpg"
```

---

### 3. ⚠️ Video State Management

**مشکل**: 
```typescript
const [isVideoPlaying, setIsVideoPlaying] = useState(true)
```

این state برای همه اسلایدها مشترک است.

**راه‌حل**:
```typescript
const [videoStates, setVideoStates] = useState<Record<string, boolean>>({})

const isVideoPlaying = videoStates[currentSlideData?.id] ?? true

const toggleVideo = (slideId: string) => {
  setVideoStates(prev => ({
    ...prev,
    [slideId]: !prev[slideId]
  }))
}
```

---

### 4. ⚠️ Video Controls Logic

**مشکل**: دکمه کنترل فقط زمانی نمایش داده می‌شود که `show_video_controls` true باشد.

**راه‌حل**: همیشه یک دکمه play/pause نمایش داده شود (مگر اینکه controls خود ویدیو فعال باشد).

---

### 5. ⚠️ Video Error Handling

**مشکل**: هیچ error handling برای ویدیو وجود ندارد.

**راه‌حل**: اضافه کردن error state و fallback به تصویر.

---

## 🛠️ کد اصلاح شده

### فایل: `frontend/components/home/HeroSection.tsx`

#### 1. اصلاح VideoPlayer Component

```typescript
const VideoPlayer = ({
  src,
  poster,
  autoplay,
  muted,
  loop,
  controls,
  className,
  onError
}: {
  src: string
  poster?: string
  autoplay: boolean
  muted: boolean
  loop: boolean
  controls: boolean
  className?: string
  onError?: () => void
}) => {
  const videoRef = useRef<HTMLVideoElement>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const video = videoRef.current
    if (video && autoplay) {
      video.play().catch((error) => {
        console.error('Autoplay failed:', error)
        // Autoplay failed, user interaction required
      })
    }
  }, [autoplay, src])

  return (
    <>
      {isLoading && (
        <div className="absolute inset-0 flex items-center justify-center bg-gray-900/50">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-white"></div>
        </div>
      )}
      <video
        ref={videoRef}
        src={src}
        poster={poster}
        autoPlay={autoplay}
        muted={muted}
        loop={loop}
        controls={controls}
        playsInline
        className={className}
        style={{ width: '100%', height: '100%', objectFit: 'cover' }}
        onLoadedData={() => setIsLoading(false)}
        onWaiting={() => setIsLoading(true)}
        onPlaying={() => setIsLoading(false)}
        onError={(e) => {
          console.error('Video error:', e)
          setIsLoading(false)
          onError?.()
        }}
      />
    </>
  )
}
```

#### 2. اصلاح State Management

```typescript
export default function HeroSection() {
  // ... existing states ...
  
  // Video states per slide
  const [videoStates, setVideoStates] = useState<Record<string, boolean>>({})
  const [videoErrors, setVideoErrors] = useState<Record<string, boolean>>({})
  
  // Get current video state
  const currentVideoPlaying = videoStates[currentSlideData?.id] ?? true
  const currentVideoError = videoErrors[currentSlideData?.id] ?? false
  
  // Toggle video playback
  const toggleVideoPlayback = (slideId: string) => {
    setVideoStates(prev => ({
      ...prev,
      [slideId]: !prev[slideId]
    }))
    
    // Also control the actual video element
    const videoElement = document.querySelector(`video[data-slide-id="${slideId}"]`) as HTMLVideoElement
    if (videoElement) {
      if (videoStates[slideId]) {
        videoElement.pause()
      } else {
        videoElement.play().catch(console.error)
      }
    }
  }
  
  // Handle video error
  const handleVideoError = (slideId: string) => {
    setVideoErrors(prev => ({
      ...prev,
      [slideId]: true
    }))
  }
  
  // ... rest of component ...
}
```

#### 3. اصلاح منطق hasVideo

```typescript
// در renderSlideContent() و سایر جاها:

// بهتر است این منطق را در یک useMemo قرار دهیم
const hasVideo = useMemo(() => {
  if (!currentSlideData) return false
  
  return (
    currentSlideData.video_type !== 'none' &&
    (
      (currentSlideData.video_type === 'file' && currentSlideData.video_file_url) ||
      (currentSlideData.video_type === 'url' && currentSlideData.video_url)
    )
  )
}, [currentSlideData])

const videoSrc = useMemo(() => {
  if (!hasVideo || !currentSlideData) return ""
  return currentSlideData.video_file_url || currentSlideData.video_url || ""
}, [hasVideo, currentSlideData])

const videoPoster = useMemo(() => {
  return currentSlideData?.video_thumbnail_url || 
         currentHeroSlide?.desktop_image_url || 
         siteSettings?.default_hero_image_url || 
         "/images/hero-main.jpg"
}, [currentSlideData, currentHeroSlide, siteSettings])
```

#### 4. اصلاح استفاده از VideoPlayer

```typescript
// در case 1 و سایر جاها:

{hasVideo && !currentVideoError ? (
  <VideoPlayer
    src={videoSrc}
    poster={videoPoster}
    autoplay={currentSlideData?.is_video_autoplay_allowed || false}
    muted={currentSlideData?.video_muted ?? true}
    loop={currentSlideData?.video_loop ?? true}
    controls={currentSlideData?.show_video_controls ?? false}
    className="w-full h-full object-cover"
    onError={() => handleVideoError(currentSlideData?.id || '')}
  />
) : (
  <OptimizedImage
    src={currentHeroSlide?.desktop_image_url || siteSettings?.default_hero_image_url || "/images/hero-main.jpg"}
    alt="Hero Background"
    fill
    className="object-cover"
    quality={85}
    sizes="100vw"
    placeholder="blur"
    blurDataURL="data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAYEBQYFBAYGBQYHBwYIChAKCgkJChQODwwQFxQYGBcUFhYaHSUfGhsjHBYWICwgIyYnKSopGR8tMC0oMCUoKSj/2wBDAQcHBwoIChMKChMoGhYaKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCgoKCj/wAARCAAIAAoDASIAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAAAAv/xAAhEAACAQMDBQAAAAAAAAAAAAABAgMABAUGIWGRkqGx0f/EABUBAQEAAAAAAAAAAAAAAAAAAAMF/8QAGhEAAgIDAAAAAAAAAAAAAAAAAAECEgMRkf/aAAwDAQACEQMRAD8AltJagyeH0AthI5xdrLcNM91BF5pX2HaH9bcfaSXWGaRmknyJckliyjqTzSlT54b6bk+h0R//2Q=="
    fallbackSrc="/images/hero-main.jpg"
  />
)}

{/* Video Control Button - نمایش همیشگی */}
{hasVideo && !currentVideoError && !currentSlideData?.show_video_controls && (
  <motion.button
    onClick={() => toggleVideoPlayback(currentSlideData?.id || '')}
    className="absolute top-4 right-4 w-12 h-12 bg-black/50 hover:bg-black/70 backdrop-blur-sm rounded-full flex items-center justify-center text-white transition-all duration-300 hover:scale-110 z-20"
    whileHover={{ scale: 1.1 }}
    whileTap={{ scale: 0.9 }}
    aria-label={currentVideoPlaying ? 'Pause video' : 'Play video'}
  >
    {currentVideoPlaying ? <FaPause className="w-5 h-5" /> : <FaPlay className="w-5 h-5 ml-0.5" />}
  </motion.button>
)}

{/* Error Message */}
{currentVideoError && (
  <div className="absolute top-4 left-4 bg-red-500/80 text-white px-4 py-2 rounded-lg">
    Failed to load video. Showing image instead.
  </div>
)}
```

---

## 📝 تغییرات لازم در بک‌اند

### هیچ تغییری لازم نیست! ✅

بک‌اند به خوبی طراحی شده و تمام فیلدهای لازم را ارائه می‌دهد. تنها کاری که باید انجام شود، اطمینان از تنظیمات صحیح در admin است.

---

## 🧪 تست

### چک‌لیست تست:

#### تست 1: اسلاید با تصویر
- [ ] تصویر به درستی نمایش داده می‌شود
- [ ] تصویر responsive است (mobile, tablet, desktop)
- [ ] دکمه‌ها کار می‌کنند
- [ ] انیمیشن‌ها smooth هستند

#### تست 2: اسلاید با ویدیو (فایل)
- [ ] ویدیو به درستی نمایش داده می‌شود
- [ ] Autoplay کار می‌کند (اگر muted باشد)
- [ ] دکمه play/pause کار می‌کند
- [ ] Loop کار می‌کند
- [ ] Thumbnail قبل از بارگذاری نمایش داده می‌شود
- [ ] Loading indicator نمایش داده می‌شود

#### تست 3: اسلاید با ویدیو (URL)
- [ ] ویدیو از URL خارجی بارگذاری می‌شود
- [ ] همه تست‌های بالا ✅

#### تست 4: Error Handling
- [ ] اگر ویدیو بارگذاری نشود، تصویر نمایش داده می‌شود
- [ ] پیام خطا نمایش داده می‌شود
- [ ] اسلایدر crash نمی‌کند

#### تست 5: Performance
- [ ] تعویض اسلایدها smooth است
- [ ] ویدیوها به موقع متوقف می‌شوند
- [ ] Memory leak وجود ندارد

---

## 🚀 مراحل اعمال تغییرات

### گام 1: Backup

```bash
# Backup فایل فعلی
cp frontend/components/home/HeroSection.tsx frontend/components/home/HeroSection.tsx.backup
```

### گام 2: اعمال تغییرات

تغییرات بالا را در فایل `HeroSection.tsx` اعمال کنید.

### گام 3: تست در محیط Development

```bash
cd frontend
npm run dev
```

مرورگر را باز کنید و تست کنید.

### گام 4: بررسی Console

F12 > Console را باز کنید و بررسی کنید که خطایی وجود ندارد.

### گام 5: تست در مرورگرهای مختلف

- Chrome ✅
- Firefox ✅
- Safari ✅
- Edge ✅
- Mobile browsers ✅

### گام 6: Deploy

اگر همه چیز OK بود:

```bash
npm run build
```

---

## 📊 نتایج مورد انتظار

بعد از اعمال این تغییرات:

### ✅ بهبودها:

1. **Reliability**: ویدیوها به طور قابل اعتماد نمایش داده می‌شوند
2. **Error Handling**: خطاها به خوبی مدیریت می‌شوند
3. **User Experience**: کاربر همیشه کنترل دارد
4. **Performance**: بهینه‌تر و سریع‌تر
5. **Maintainability**: کد تمیزتر و قابل نگهداری‌تر

### ✅ مشکلات برطرف شده:

1. ✅ ویدیوها به درستی نمایش داده می‌شوند
2. ✅ Fallback ها صحیح کار می‌کنند
3. ✅ Video state برای هر اسلاید جداگانه است
4. ✅ Error handling وجود دارد
5. ✅ Loading state نمایش داده می‌شود

---

## 🎯 نتیجه‌گیری

با اعمال این تغییرات، Hero Slider به یک کامپوننت کاملاً قابل اعتماد و حرفه‌ای تبدیل می‌شود که:

- ✅ از تصاویر و ویدیو پشتیبانی می‌کند
- ✅ خطاها را به خوبی مدیریت می‌کند
- ✅ تجربه کاربری عالی ارائه می‌دهد
- ✅ Performance بهینه دارد
- ✅ قابل نگهداری است

**توصیه**: این تغییرات را در یک branch جداگانه اعمال کنید و بعد از تست کامل، merge کنید.

```bash
git checkout -b fix/hero-slider-improvements
# اعمال تغییرات
git add .
git commit -m "Fix: Improve Hero Slider video handling and error management"
git push origin fix/hero-slider-improvements
# ایجاد Pull Request
```
