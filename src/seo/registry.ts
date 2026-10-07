import { SeoPageRecord } from './registry.types';

export const GlobalSeoRegistry: Record<string, SeoPageRecord> = {
  home: {
    route: '/',
    locale: 'tr-TR',
    role: 'home',
    indexDirective: 'index, follow',
    canonicalRoute: '/',
    title: 'InversionCore | Negatif Bilgi & Tersine Mühendislik',
    metaDescription: 'Barış Bağırlar Web Ekosistemi: Davranışsal Tersine Mühendislik ve Bilişsel Karar Platformu.',
    h1: 'INVERSIONCORE',
    primaryIntent: 'brand_navigation',
    primaryEntity: {
      id: 'https://inversioncore.com/#organization',
      name: 'InversionCore',
      type: 'Organization',
      sameAs: ['https://barisbagirlar.com']
    },
    semanticTriples: [
      { subject: 'InversionCore', predicate: 'providesService', object: 'Bilişsel Tersine Mühendislik' }
    ],
    heroAnswerEngine: 'InversionCore, bireylerin ve şirketlerin bilişsel kör noktalarını, rasyonelleştirilmiş mazeretlerini ve karar mekanizmalarındaki asalak yükleri açığa çıkaran Davranışsal Tersine Mühendislik ve Negatif Bilgi (Via Negativa) platformudur.',
    publishedAt: '2026-10-01T00:00:00Z',
    modifiedAt: '2026-10-07T00:00:00Z',
    bodyContentHash: 'a591a6d40bf420404a011733cfb7b190d62c65bf0bc9c24db3370e75b70d4812',
    llmSubGraphRoute: '/llms/pages/home.md',
    mobileSubGraphRoute: '/llms/mobile/home.md',
    breadcrumbs: [{ name: 'Ana Sayfa', item: '/' }],
    mobile: {
      viewport: 'width=device-width, initial-scale=1, viewport-fit=cover, minimum-scale=1, maximum-scale=5',
      primaryAction: 'navigate',
      bottomNavEnabled: true,
      thumbZonePosition: 'bottom-center',
      touchTargetsValidated: true,
      horizontalScrollFree: true,
      thumbSafeHeroAnswer: true,
      voiceQueryPatterns: ['InversionCore nedir?'],
      speakableSelectors: ['#aeo-answer-block'],
      pwaInstallable: true
    },
    mobileCwvBudget: { lcpMs: 1800, inpMs: 100, cls: 0.03, ttfbMs: 150, htmlKb: 50 }
  }
};
