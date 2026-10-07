import { SeoPageRecord } from './registry.types';
export function buildCompleteJsonLdGraph(page: SeoPageRecord, domain: string): string {
  const origin = `https://${domain}`;
  const pageUrl = `${origin}${page.route === '/' ? '' : page.route}`;
  const graph: Record<string, any>[] = [
    {
      '@type': 'Organization',
      '@id': `${origin}/#organization`,
      name: 'Global Enterprise Master',
      url: origin,
      logo: { '@type': 'ImageObject', '@id': `${origin}/#logo`, url: `${origin}/assets/logo.png` },
      sameAs: page.primaryEntity.sameAs
    },
    {
      '@type': 'WebSite',
      '@id': `${origin}/#website`,
      url: origin,
      name: 'Global Enterprise Master',
      publisher: { '@id': `${origin}/#organization` },
      inLanguage: page.locale,
      potentialAction: {
        '@type': 'SearchAction',
        target: { '@type': 'EntryPoint', urlTemplate: `${origin}/ara?q={search_term_string}` },
        'query-input': 'required name=search_term_string'
      }
    },
    {
      '@type': 'WebPage',
      '@id': `${pageUrl}#webpage`,
      url: pageUrl,
      name: page.title,
      description: page.metaDescription,
      isPartOf: { '@id': `${origin}/#website` },
      about: { '@id': page.primaryEntity.id },
      datePublished: page.publishedAt,
      dateModified: page.modifiedAt,
      breadcrumb: { '@id': `${pageUrl}#breadcrumb` },
      inLanguage: page.locale,
      speakable: { '@type': 'SpeakableSpecification', cssSelector: page.mobile.speakableSelectors },
      potentialAction: {
        '@type': page.mobile.primaryAction === 'call' ? 'CommunicateAction' : 'ViewAction',
        target: page.mobile.primaryAction === 'call' ? 'tel:+900000000000' : pageUrl
      }
    },
    {
      '@type': 'BreadcrumbList',
      '@id': `${pageUrl}#breadcrumb`,
      itemListElement: page.breadcrumbs.map((b, idx) => ({
        '@type': 'ListItem', position: idx + 1, name: b.name, item: b.item.startsWith('http') ? b.item : `${origin}${b.item}`
      }))
    }
  ];
  return JSON.stringify({ '@context': 'https://schema.org', '@graph': graph });
}
