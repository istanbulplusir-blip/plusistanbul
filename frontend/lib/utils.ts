import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';
import { getValidatedImageUrl } from './imageValidation';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function getImageUrl(imagePath: string | undefined): string {
  return getValidatedImageUrl(imagePath);
}