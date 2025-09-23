import { apiClient } from './client'

// Types for shared API responses
export interface HeroSlide {
  id: string
  title: string
  subtitle: string
  description: string
  button_text: string
  button_url: string
  button_type: 'primary' | 'secondary' | 'outline'
  desktop_image: string
  tablet_image: string
  mobile_image: string
  desktop_image_url: string
  tablet_image_url: string
  mobile_image_url: string
  order: number
  display_duration: number
  show_for_authenticated: boolean
  show_for_anonymous: boolean
  start_date?: string
  end_date?: string
  is_active: boolean
  is_active_now: boolean
  view_count: number
  click_count: number
  click_rate: number
  created_at: string
  updated_at: string
  // Video fields
  video_type: 'none' | 'file' | 'url'
  video_file?: string
  video_url?: string
  video_thumbnail?: string
  video_file_url?: string
  video_thumbnail_url?: string
  has_video: boolean
  video_display_name: string
  autoplay_video: boolean
  video_muted: boolean
  show_video_controls: boolean
  video_loop: boolean
  is_video_autoplay_allowed: boolean
}

export interface Banner {
  id: string
  title: string
  alt_text: string
  banner_type: 'homepage_top' | 'homepage_bottom' | 'tour_detail' | 'event_detail' | 'seasonal' | 'promotion' | 'sidebar' | 'popup'
  position: 'top' | 'middle' | 'bottom' | 'sidebar' | 'popup'
  image: string
  mobile_image?: string
  image_url: string
  mobile_image_url?: string
  link_url?: string
  link_target: '_self' | '_blank'
  display_order: number
  start_date?: string
  end_date?: string
  show_on_pages: string[]
  show_for_authenticated: boolean
  show_for_anonymous: boolean
  is_active: boolean
  is_active_now: boolean
  view_count: number
  click_count: number
  click_rate: number
  created_at: string
  updated_at: string
}

export interface SiteSettings {
  id: string
  site_name: string
  site_description: string
  default_language: string
  default_phone?: string
  default_email?: string
  default_hero_image?: string
  default_tour_image?: string
  default_event_image?: string
  default_meta_image?: string
  default_hero_image_url?: string
  default_tour_image_url?: string
  default_event_image_url?: string
  default_meta_image_url?: string
  maintenance_mode: boolean
  maintenance_message?: string
  default_meta_title?: string
  default_meta_description?: string
  created_at: string
  updated_at: string
}

// New homepage section interfaces
export interface AboutSection {
  id: number;
  title: string;
  subtitle: string;
  description: string;
  button_text: string;
  button_url: string;
  hero_image?: string;
  hero_image_url?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface AboutStatistic {
  id: number;
  label: string;
  description?: string;
  value: string;
  icon: string;
  order: number;
  is_active: boolean;
}

export interface AboutFeature {
  id: number;
  title: string;
  description?: string;
  icon: string;
  order: number;
  is_active: boolean;
}

export interface CTASection {
  id: number;
  title: string;
  subtitle: string;
  description: string;
  background_image?: string;
  background_image_url?: string;
  buttons: CTAButton[];
  features: CTAFeature[];
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface CTAButton {
  id: number;
  text: string;
  url: string;
  button_type: string;
  order: number;
  is_active: boolean;
}

export interface CTAFeature {
  id: number;
  text: string;
  icon: string;
  order: number;
  is_active: boolean;
}

export interface Footer {
  id: number;
  newsletter_title: string;
  newsletter_description: string;
  company_name: string;
  company_description: string;
  copyright_text: string;
  newsletter_placeholder: string;
  trusted_by_text: string;
  logo?: string;
  logo_url?: string;
  default_phone?: string;
  default_email?: string;
  instagram_url?: string;
  telegram_url?: string;
  whatsapp_number?: string;
  facebook_url?: string;
  navigation_links: FooterLink[];
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface FooterLink {
  id: number;
  label: string;
  url: string;
  link_type: string;
  order: number;
  is_active: boolean;
}

export interface TransferBookingSection {
  id: number;
  title: string;
  subtitle: string;
  description: string;
  button_text: string;
  button_url: string;
  background_image?: string;
  background_image_url?: string;
  experience_years: number;
  countries_served: number;
  feature_1: string;
  feature_2: string;
  feature_3: string;
  feature_4: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface WhatsAppInfo {
  phone: string;
  formatted_phone: string;
  whatsapp_url: string;
  display_phone: string;
}

export interface FAQSettings {
  id: number;
  title: string;
  subtitle: string;
  items_per_page: number;
  show_categories: boolean;
  show_search: boolean;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

// API functions
export const getHeroSlides = async (): Promise<HeroSlide[]> => {
  try {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const response = await apiClient.get('/shared/hero-slides/active/') as any
    return response.data
  } catch (error) {
    console.error('Error fetching hero slides:', error)
    return []
  }
}

export const getBanners = async (page?: string): Promise<Banner[]> => {
  try {
    const params = page ? { page } : {}
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const response = await apiClient.get('/shared/banners/active/', { params }) as any
    return response.data
  } catch (error) {
    console.error('Error fetching banners:', error)
    return []
  }
}

export const getSiteSettings = async (): Promise<SiteSettings | null> => {
  try {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const response = await apiClient.get('/shared/site-settings/') as any
    return response.data
  } catch (error) {
    console.error('Error fetching site settings:', error)
    return null
  }
}

export const trackHeroSlideClick = async (slideId: string): Promise<boolean> => {
  try {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    await apiClient.post(`/shared/hero-slides/${slideId}/track_click/`) as any
    return true
  } catch (error) {
    console.error('Error tracking hero slide click:', error)
    return false
  }
}

export const trackHeroSlideView = async (slideId: string): Promise<boolean> => {
  try {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    await apiClient.post(`/shared/hero-slides/${slideId}/track_view/`) as any
    return true
  } catch (error) {
    console.error('Error tracking hero slide view:', error)
    return false
  }
}

export const trackBannerClick = async (bannerId: string): Promise<boolean> => {
  try {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    await apiClient.post(`/shared/banners/${bannerId}/track_click/`) as any
    return true
  } catch (error) {
    console.error('Error tracking banner click:', error)
    return false
  }
}

export const trackBannerView = async (bannerId: string): Promise<boolean> => {
  try {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    await apiClient.post(`/shared/banners/${bannerId}/track_view/`) as any
    return true
  } catch (error) {
    console.error('Error tracking banner view:', error)
    return false
  }
}

// New homepage section API functions
export const getAboutSection = async (): Promise<AboutSection | null> => {
  try {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const response = await apiClient.get('/shared/about-section/active/') as any
    return response.data
  } catch (error) {
    console.error('Error fetching about section:', error)
    return null
  }
}

export const getAboutStatistics = async (): Promise<AboutStatistic[]> => {
  try {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const response = await apiClient.get('/shared/about-statistics/') as any
    return response.data.results || response.data || []
  } catch (error) {
    console.error('Error fetching about statistics:', error)
    return []
  }
}

export const getAboutFeatures = async (): Promise<AboutFeature[]> => {
  try {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const response = await apiClient.get('/shared/about-features/') as any
    return response.data.results || response.data || []
  } catch (error) {
    console.error('Error fetching about features:', error)
    return []
  }
}

export const getCTASection = async (): Promise<CTASection | null> => {
  try {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const response = await apiClient.get('/shared/cta-section/active/') as any
    return response.data
  } catch (error) {
    console.error('Error fetching CTA section:', error)
    return null
  }
}

export const getFooter = async (): Promise<Footer | null> => {
  try {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const response = await apiClient.get('/shared/footer/active/') as any
    return response.data
  } catch (error) {
    console.error('Error fetching footer:', error)
    return null
  }
}

export const getTransferBookingSection = async (): Promise<TransferBookingSection | null> => {
  try {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const response = await apiClient.get('/shared/transfer-booking-section/active/') as any
    return response.data
  } catch (error) {
    console.error('Error fetching transfer booking section:', error)
    return null
  }
}

export const getWhatsAppInfo = async (): Promise<WhatsAppInfo | null> => {
  try {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const response = await apiClient.get('/shared/whatsapp-info/') as any
    return response.data
  } catch (error) {
    console.error('Error fetching WhatsApp info:', error)
    return null
  }
}

export const getFAQSettings = async (): Promise<FAQSettings | null> => {
  try {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const response = await apiClient.get('/shared/faq-settings/') as any
    // Return the first active FAQ settings
    const activeSettings = response.data?.results?.find((setting: { is_active: boolean }) => setting.is_active) || response.data?.results?.[0]
    return activeSettings || null
  } catch (error) {
    console.error('Error fetching FAQ settings:', error)
    return null
  }
}
