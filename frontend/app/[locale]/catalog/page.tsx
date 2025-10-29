import { Metadata } from 'next';
import { getTranslations } from 'next-intl/server';
import CatalogViewer from '../../../components/catalog/CatalogViewer';

type Props = {
    params: Promise<{ locale: string }>;
};

export async function generateMetadata({ params }: Props): Promise<Metadata> {
    const { locale } = await params;
    const t = await getTranslations({ locale, namespace: 'catalog' });

    return {
        title: t('meta.title'),
        description: t('meta.description'),
        openGraph: {
            title: t('meta.title'),
            description: t('meta.description'),
            type: 'website',
        },
    };
}

export default function CatalogPage() {
    return (
        <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-teal-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
            <div className="section-container section-padding">
                <div className="max-w-7xl mx-auto">
                    <CatalogViewer />
                </div>
            </div>
        </div>
    );
}
