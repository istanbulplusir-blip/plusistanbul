'use client';

import { useState, useEffect } from 'react';
import { useTranslations } from 'next-intl';
import { motion } from 'framer-motion';
import { Download, FileText, Loader2 } from 'lucide-react';
import { apiClient } from '../../lib/api/client';

interface CatalogFile {
    id: number;
    title: string;
    description: string;
    file_url: string;
    download_url: string;
    version: string;
    file_size_mb: string;
    catalog_type: string;
    is_featured: boolean;
}

export default function CatalogViewer() {
    const t = useTranslations('catalog');
    const [catalog, setCatalog] = useState<CatalogFile | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        fetchFeaturedCatalog();
    }, []);

    const fetchFeaturedCatalog = async () => {
        try {
            setLoading(true);
            setError(null);

            const response = await apiClient.get('/shared/catalogs/featured/') as { data: CatalogFile };
            const catalogData = response.data;

            setCatalog(catalogData);

            // Track view
            if (catalogData?.id) {
                trackView(catalogData.id);
            }
        } catch (err) {
            console.error('Error fetching catalog:', err);
            setError(t('error'));
        } finally {
            setLoading(false);
        }
    };

    const trackView = async (catalogId: number) => {
        try {
            await apiClient.post(`/shared/catalogs/${catalogId}/track_view/`);
        } catch (err) {
            console.error('Error tracking view:', err);
        }
    };

    const handleDownload = () => {
        if (catalog?.download_url) {
            window.open(catalog.download_url, '_blank');
        }
    };

    if (loading) {
        return (
            <div className="flex flex-col items-center justify-center min-h-[400px]">
                <Loader2 className="w-12 h-12 animate-spin text-primary mb-4" />
                <p className="text-gray-600 dark:text-gray-300">{t('loading')}</p>
            </div>
        );
    }

    if (error || !catalog) {
        return (
            <div className="flex flex-col items-center justify-center min-h-[400px]">
                <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-6 max-w-md text-center">
                    <p className="text-red-600 dark:text-red-400">{error || t('error')}</p>
                </div>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            {/* Catalog Info Card */}
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6 }}
                className="card p-6"
            >
                <div className="flex items-start justify-between flex-wrap gap-4">
                    <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-3 mb-2">
                            <FileText className="w-6 h-6 text-primary flex-shrink-0" />
                            <h1 className="heading-2 truncate">{catalog.title}</h1>
                        </div>
                        {catalog.description && (
                            <p className="body-text mb-4">{catalog.description}</p>
                        )}
                        <div className="flex flex-wrap gap-4 text-sm text-gray-600 dark:text-gray-300">
                            {catalog.version && (
                                <div>
                                    <span className="font-medium">{t('version')}:</span> {catalog.version}
                                </div>
                            )}
                            {catalog.file_size_mb && (
                                <div>
                                    <span className="font-medium">{t('fileSize')}:</span> {catalog.file_size_mb} MB
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Download Button - Desktop */}
                    <button
                        onClick={handleDownload}
                        className="hidden md:flex items-center gap-2 px-6 py-3 bg-primary text-white rounded-lg hover:bg-primary-dark transition-colors font-medium"
                    >
                        <Download className="w-5 h-5" />
                        {t('download')}
                    </button>
                </div>
            </motion.div>

            {/* PDF Viewer */}
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: 0.2 }}
                className="card p-4 md:p-6"
            >
                <div className="mb-4">
                    <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                        {t('preview')}
                    </h2>
                </div>
                <div className="relative w-full" style={{ height: '70vh', minHeight: '500px' }}>
                    <iframe
                        src={catalog.file_url}
                        className="w-full h-full border-0 rounded-lg"
                        title={catalog.title}
                    />
                </div>
            </motion.div>

            {/* Fixed Download Button - Mobile */}
            <div className="md:hidden fixed bottom-6 left-1/2 transform -translate-x-1/2 z-50">
                <button
                    onClick={handleDownload}
                    className="flex items-center gap-2 px-8 py-4 bg-primary text-white rounded-full hover:bg-primary-dark transition-colors font-medium shadow-lg"
                >
                    <Download className="w-5 h-5" />
                    {t('download')}
                </button>
            </div>
        </div>
    );
}
