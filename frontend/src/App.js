import { useState } from 'react';
import '@/App.css';
import { Header, Footer } from '@/components/site/Layout';
import { Hero } from '@/components/site/Hero';
import { Services } from '@/components/site/Services';
import { Process, ContactBanner } from '@/components/site/Sections';
import { InquiryDialog } from '@/components/site/InquiryDialog';
import { ContentDialog } from '@/components/site/ContentDialog';

export default function App() {
  const [inquiry, setInquiry] = useState(null);
  const [content, setContent] = useState(null);
  const request = (material = 'offen') => { setContent(null); setInquiry(material); };
  return (
    <>
      <a className="skip-link" href="#leistungen" data-testid="skip-to-content">Zum Inhalt</a>
      <Header onRequest={() => request()} onContent={setContent} />
      <main>
        <Hero onRequest={() => request()} onExamples={() => setContent({ type: 'examples' })} />
        <Services onSelect={service => setContent({ type: 'service', service })} />
        <Process />
        <ContactBanner onRequest={() => request()} />
      </main>
      <Footer onContent={setContent} />
      <ContentDialog content={content} onClose={() => setContent(null)} onRequest={request} onSelect={service => setContent(service ? { type: 'service', service } : { type: 'examples' })} />
      <InquiryDialog material={inquiry} onClose={() => setInquiry(null)} />
    </>
  );
}