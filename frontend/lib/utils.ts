import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function getImageUrl(imagePath: string | undefined): string {
  if (!imagePath) return '/images/placeholder.jpg';
  if (imagePath.startsWith('http')) return imagePath;
  return `/images/${imagePath}`;
}