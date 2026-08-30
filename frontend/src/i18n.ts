import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

import enJSON from './locales/en.json';
import hiJSON from './locales/hi.json';

const resources = {
    en: { translation: enJSON },
    hi: { translation: hiJSON },
} as const;

i18n
    .use(LanguageDetector)
    .use(initReactI18next)
    .init({
        resources,
        fallbackLng: 'en',
        interpolation: { escapeValue: false }
    });

i18n.on('languageChanged', async (lng: string) => {

    if (!Object.keys(resources).includes(lng)) {
        try {
            // NOTE: Replace URL with API endpoint
            const response = await fetch(`http://localhost:8080/api/translations/static?lang=${lng}`);
            const dbTranslations = await response.json();

            i18n.addResourceBundle(lng, 'translation', dbTranslations, true, true);
        } catch (error) {
            console.error(`Failed to load translations for ${lng} from DB`, error);
        }
    }
});

export default i18n;