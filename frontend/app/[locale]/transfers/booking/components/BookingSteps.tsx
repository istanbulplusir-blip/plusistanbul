'use client';

import React, { useState, useEffect } from 'react';

import { CheckCircle } from 'lucide-react';
import { BookingStep } from '@/lib/types/transfers';
import { UI_CLASSES } from '@/lib/constants/ui';

interface Step {
  key: BookingStep;
  title: string;
  description: string;
}

interface BookingStepsProps {
  steps: Step[];
  currentStep: BookingStep;
  onStepClick: (step: BookingStep) => void;
  isStepValid: (step: BookingStep) => boolean;
}

export default function BookingSteps({ steps, currentStep, onStepClick, isStepValid }: BookingStepsProps) {
  const [isClient, setIsClient] = useState(false);

  useEffect(() => {
    setIsClient(true);
  }, []);

  const getStepStatus = (step: Step) => {
    const currentIndex = steps.findIndex(s => s.key === currentStep);
    const stepIndex = steps.findIndex(s => s.key === step.key);
    
    if (stepIndex < currentIndex) {
      return 'completed';
    } else if (stepIndex === currentIndex) {
      return 'current';
    } else {
      return 'upcoming';
    }
  };

  // Don't render until client-side to prevent hydration mismatch
  if (!isClient) {
    return (
      <div className={UI_CLASSES.card}>
        <div className={UI_CLASSES.flexBetween}>
          {steps.map((step, index) => (
            <div key={step.key} className={UI_CLASSES.flexStart}>
              <div className={`w-10 h-10 rounded-full bg-gray-200 dark:bg-gray-600 ${UI_CLASSES.flexCenter}`}>
                <span className={`${UI_CLASSES.smallText} font-medium ${UI_CLASSES.textPrimary}`}>{index + 1}</span>
              </div>
              <div className="ml-3">
                <h3 className={`${UI_CLASSES.smallText} font-medium ${UI_CLASSES.textPrimary}`}>{step.title}</h3>
                <p className={UI_CLASSES.caption}>{step.description}</p>
              </div>
              {index < steps.length - 1 && (
                <div className="flex-1 h-0.5 mx-4 bg-gray-200 dark:bg-gray-600" />
              )}
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className={UI_CLASSES.card}>
      <div className={UI_CLASSES.flexBetween}>
        {steps.map((step, index) => {
          const status = getStepStatus(step);
          const isCompleted = status === 'completed';
          const isCurrent = status === 'current';
          const currentIndex = steps.findIndex(s => s.key === currentStep);
          const stepIndex = steps.findIndex(s => s.key === step.key);
          
          // Only allow clicking on:
          // 1. Previous steps (completed)
          // 2. Current step
          // 3. Next step (only if current step is valid)
          const canClick = Boolean(
            isCompleted || 
            isCurrent || 
            (stepIndex === currentIndex + 1 && isStepValid(currentStep))
          );
          
          return (
            <div key={step.key} className="flex items-center">
              {/* Step Circle */}
              <button
                onClick={() => canClick && onStepClick(step.key)}
                disabled={!canClick}
                className={`
                  w-10 h-10 rounded-full flex items-center justify-center transition-all
                  ${isCompleted
                    ? 'bg-green-500 text-white'
                    : isCurrent
                    ? 'bg-blue-500 text-white'
                    : canClick
                    ? 'bg-gray-200 text-gray-600 hover:bg-gray-300'
                    : 'bg-gray-100 text-gray-400 cursor-not-allowed'
                  }
                `}
              >
                {isCompleted ? (
                  <CheckCircle className="w-5 h-5" />
                ) : (
                  <span className="text-sm font-medium">{index + 1}</span>
                )}
              </button>
              
              {/* Step Info */}
              <div className="ml-3">
                <h3 className={`
                  text-sm font-medium
                  ${isCompleted
                    ? 'text-green-600 dark:text-green-400'
                    : isCurrent
                    ? 'text-blue-600 dark:text-blue-400'
                    : canClick
                    ? 'text-gray-900 dark:text-gray-100'
                    : 'text-gray-400 dark:text-gray-500'
                  }
                `}>
                  {step.title}
                </h3>
                <p className={`
                  text-xs
                  ${isCompleted
                    ? 'text-green-500 dark:text-green-300'
                    : isCurrent
                    ? 'text-blue-500 dark:text-blue-300'
                    : canClick
                    ? 'text-gray-600 dark:text-gray-400'
                    : 'text-gray-400 dark:text-gray-500'
                  }
                `}>
                  {step.description}
                </p>
              </div>
              
              {/* Connector Line */}
              {index < steps.length - 1 && (
                <div className={`
                  flex-1 h-0.5 mx-4
                  ${isCompleted ? 'bg-green-500 dark:bg-green-400' : 'bg-gray-200 dark:bg-gray-600'}
                `} />
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
} 