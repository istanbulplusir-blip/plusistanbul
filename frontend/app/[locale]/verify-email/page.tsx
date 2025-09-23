'use client';

import { useState, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { useTranslations } from 'next-intl';
import Link from 'next/link';
import { Mail, CheckCircle, XCircle, ArrowRight } from 'lucide-react';

export default function VerifyEmailPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const t = useTranslations('auth');
  
  const [otpCode, setOtpCode] = useState('');
  const [email, setEmail] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isResending, setIsResending] = useState(false);
  const [message, setMessage] = useState('');
  const [messageType, setMessageType] = useState<'success' | 'error' | ''>('');
  const [countdown, setCountdown] = useState(0);

  useEffect(() => {
    // Get email from URL params or localStorage
    const emailFromParams = searchParams.get('email');
    const emailFromStorage = localStorage.getItem('pendingEmailVerification');
    
    if (emailFromParams) {
      setEmail(emailFromParams);
      localStorage.setItem('pendingEmailVerification', emailFromParams);
    } else if (emailFromStorage) {
      setEmail(emailFromStorage);
    }
  }, [searchParams]);

  useEffect(() => {
    let timer: NodeJS.Timeout;
    if (countdown > 0) {
      timer = setTimeout(() => setCountdown(countdown - 1), 1000);
    }
    return () => clearTimeout(timer);
  }, [countdown]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!otpCode || !email) {
      setMessage(t('pleaseFillAllFields'));
      setMessageType('error');
      return;
    }

    setIsLoading(true);
    setMessage('');

    try {
      const response = await fetch('/api/v1/auth/verify-email/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email,
          otp_code: otpCode,
        }),
      });

      const data = await response.json();

      if (response.ok) {
        setMessage(t('emailVerifiedSuccessfully'));
        setMessageType('success');
        localStorage.removeItem('pendingEmailVerification');
        
        // Redirect to login after 2 seconds
        setTimeout(() => {
          router.push('/login');
        }, 2000);
      } else {
        setMessage(data.message || t('verificationFailed'));
        setMessageType('error');
      }
    } catch {
      setMessage(t('networkError'));
      setMessageType('error');
    } finally {
      setIsLoading(false);
    }
  };

  const handleResendOTP = async () => {
    if (!email) {
      setMessage(t('pleaseEnterEmail'));
      setMessageType('error');
      return;
    }

    setIsResending(true);
    setMessage('');

    try {
      const response = await fetch('/api/v1/auth/verify-email/', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email }),
      });

      const data = await response.json();

      if (response.ok) {
        setMessage(t('verificationEmailSent'));
        setMessageType('success');
        setCountdown(60); // 60 seconds cooldown
      } else {
        setMessage(data.message || t('failedToSendEmail'));
        setMessageType('error');
      }
    } catch {
      setMessage(t('networkError'));
      setMessageType('error');
    } finally {
      setIsResending(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="max-w-md w-full space-y-8">
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8">
          {/* Header */}
          <div className="text-center mb-8">
            <div className="mx-auto w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mb-4">
              <Mail className="w-8 h-8 text-blue-600" />
            </div>
            <h2 className="text-3xl font-bold text-gray-900 mb-2">
              {t('verifyEmail')}
            </h2>
            <p className="text-gray-600">
              {t('enterVerificationCode')}
            </p>
          </div>

          {/* Message */}
          {message && (
            <div className={`mb-6 p-4 rounded-lg flex items-center space-x-3 ${
              messageType === 'success' 
                ? 'bg-green-50 text-green-800 border border-green-200' 
                : 'bg-red-50 text-red-800 border border-red-200'
            }`}>
              {messageType === 'success' ? (
                <CheckCircle className="w-5 h-5 text-green-600" />
              ) : (
                <XCircle className="w-5 h-5 text-red-600" />
              )}
              <span className="text-sm font-medium">{message}</span>
            </div>
          )}

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Email Display */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                {t('email')}
              </label>
              <div className="relative">
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder={t('enterEmail')}
                  required
                />
                <Mail className="absolute right-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
              </div>
            </div>

            {/* OTP Code */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                {t('verificationCode')}
              </label>
              <div className="relative">
                <input
                  type="text"
                  value={otpCode}
                  onChange={(e) => setOtpCode(e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent text-center text-lg font-mono tracking-widest"
                  placeholder="000000"
                  maxLength={6}
                  required
                />
              </div>
              <p className="mt-2 text-sm text-gray-500">
                {t('enter6DigitCode')}
              </p>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={isLoading}
              className="w-full bg-blue-600 text-white py-3 px-4 rounded-lg hover:bg-blue-700 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200 flex items-center justify-center space-x-2"
            >
              {isLoading ? (
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
              ) : (
                <>
                  <span>{t('verifyEmail')}</span>
                  <ArrowRight className="w-4 h-4" />
                </>
              )}
            </button>
          </form>

          {/* Resend OTP */}
          <div className="mt-6 text-center">
            <p className="text-sm text-gray-600 mb-2">
              {t('didntReceiveCode')}
            </p>
            <button
              onClick={handleResendOTP}
              disabled={isResending || countdown > 0}
              className="text-blue-600 hover:text-blue-700 font-medium disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200"
            >
              {isResending ? (
                <span className="flex items-center space-x-2">
                  <div className="w-4 h-4 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
                  <span>{t('sending')}</span>
                </span>
              ) : countdown > 0 ? (
                <span>{t('resendIn')} {countdown}s</span>
              ) : (
                <span>{t('resendCode')}</span>
              )}
            </button>
          </div>

          {/* Back to Login */}
          <div className="mt-8 text-center">
            <Link
              href="/login"
              className="text-gray-600 hover:text-gray-800 transition-colors duration-200"
            >
              {t('backToLogin')}
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
} 