'use client';

import { useEffect, useRef } from 'react';
import { googleSignIn } from '../../lib/api/auth';
import { useAuth } from '../../lib/contexts/AuthContext';

import { useTranslations } from 'next-intl';
import type { User } from '../../lib/types/api';

type Props = {
  className?: string;
  onError?: (message: string) => void;
  onSuccessRedirect?: (path: string) => void;
};

interface GoogleCredentialResponse {
  credential: string;
}

interface GoogleUserData {
  user: User;
  tokens: { access: string; refresh: string };
}

declare global {
  interface Window {
    google?: {
      accounts: {
        id: {
          initialize: (config: { client_id: string; callback: (response: GoogleCredentialResponse) => void }) => void;
          renderButton: (element: HTMLElement, options: Record<string, string>) => void;
        };
      };
    };
  }
}

export default function GoogleSignInButton({ className, onError, onSuccessRedirect }: Props) {
  const buttonRef = useRef<HTMLDivElement | null>(null);
  const { login } = useAuth();
  const t = useTranslations('auth');

  useEffect(() => {
    // Load Google script if not present
    if (!window.google) {
      const script = document.createElement('script');
      script.src = 'https://accounts.google.com/gsi/client';
      script.async = true;
      script.defer = true;
      script.onload = initialize;
      script.onerror = () => onError?.(t('googleLoadError', { default: 'Failed to load Google services. Please try again.' }));
      document.head.appendChild(script);
    } else {
      initialize();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const initialize = () => {
    const clientId = process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID;
    if (!clientId) {
      onError?.(t('googleLoadError', { default: 'Failed to load Google services. Please try again.' }));
      return;
    }
    if (window.google?.accounts?.id) {
      window.google.accounts.id.initialize({
        client_id: clientId,
        callback: handleCredential,
      });
      if (buttonRef.current) {
        window.google.accounts.id.renderButton(buttonRef.current, {
          theme: 'outline',
          size: 'large',
          shape: 'pill',
          text: 'signin_with',
          logo_alignment: 'left',
        });
      }
    }
  };

  const handleCredential = async (response: GoogleCredentialResponse) => {
    try {
      const idToken = response?.credential;
      if (!idToken) {
        onError?.(t('googleInvalidResponse', { default: 'Invalid response from server' }));
        return;
      }
      const res = await googleSignIn(idToken);
      const data = (res as { data: GoogleUserData }).data;
      if (data?.user && data?.tokens) {
        // Store tokens and user via AuthContext (this will automatically merge guest cart)
        login(data.user, data.tokens);
        
        // Get redirect parameter from URL or default to cart
        const urlParams = new URLSearchParams(window.location.search);
        const redirect = urlParams.get('redirect') || '/cart';
        
        // Redirect to the specified path or cart
        onSuccessRedirect?.(redirect);
      } else {
        onError?.(t('googleInvalidResponse', { default: 'Invalid response from server' }));
      }
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'Unknown error occurred';
      const responseError = (err as { response?: { data?: { error?: string } } })?.response?.data?.error;
      onError?.(responseError || errorMessage || t('googleSignInFailed', { default: 'Google sign-in failed' }));
    }
  };

  return (
    <div className={className}>
      <div ref={buttonRef} />
    </div>
  );
}


