'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { CheckCircle, Circle } from 'lucide-react';

interface BookingStep {
  id: number;
  title: string;
  description: string;
  isComplete: boolean;
  isActive: boolean;
}

interface BookingProgressBarProps {
  steps: BookingStep[];
  currentStep: number;
  onStepClick?: (stepId: number) => void;
}

export default function BookingProgressBar({ 
  steps, 
  onStepClick 
}: BookingProgressBarProps) {

  return (
    <div className="w-full">
      <div className="flex items-center justify-between mb-8">
        {steps.map((step, index) => (
          <div key={step.id} className="flex items-center flex-1">
            {/* Step Circle */}
            <div className="flex flex-col items-center">
              <motion.button
                onClick={() => onStepClick?.(step.id)}
                className={`
                  relative flex items-center justify-center w-10 h-10 rounded-full border-2 transition-all duration-300
                  ${step.isComplete 
                    ? 'bg-green-500 border-green-500 text-white' 
                    : step.isActive 
                      ? 'bg-blue-500 border-blue-500 text-white' 
                      : 'bg-white dark:bg-gray-800 border-gray-300 dark:border-gray-600 text-gray-500 dark:text-gray-400'
                  }
                  ${onStepClick ? 'cursor-pointer hover:scale-105' : 'cursor-default'}
                `}
                whileHover={onStepClick ? { scale: 1.05 } : {}}
                whileTap={onStepClick ? { scale: 0.95 } : {}}
              >
                {step.isComplete ? (
                  <CheckCircle className="w-5 h-5" />
                ) : (
                  <Circle className="w-5 h-5" />
                )}
              </motion.button>
              
              {/* Step Info */}
              <div className="mt-2 text-center">
                <div className={`
                  text-sm font-medium transition-colors duration-300
                  ${step.isComplete || step.isActive 
                    ? 'text-gray-900 dark:text-white' 
                    : 'text-gray-500 dark:text-gray-400'
                  }
                `}>
                  {step.title}
                </div>
                <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                  {step.description}
                </div>
              </div>
            </div>
            
            {/* Connector Line */}
            {index < steps.length - 1 && (
              <div className="flex-1 h-0.5 mx-4 bg-gray-200 dark:bg-gray-700 relative">
                <motion.div
                  className="absolute top-0 left-0 h-full bg-blue-500"
                  initial={{ width: 0 }}
                  animate={{ 
                    width: step.isComplete ? '100%' : '0%' 
                  }}
                  transition={{ duration: 0.3 }}
                />
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
