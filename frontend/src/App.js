import { useEffect, useState } from 'react';
import { BrowserRouter, Route, Routes, useLocation } from 'react-router-dom';
import '@/App.css';
import '@/styles/product-images.css';
import '@/styles/legal.css';
import { Header, Footer } from '@/components/site/Layout';
import { Hero } from '@/components/site/Hero';
import { Services } from '@/components/site/Services';
import { Process, ContactBanner } from '@/components/site/Sections';
import { InquiryDialog } from '@/components/site/InquiryDialog';
import { ContentDialog } from '@/components/site/ContentDialog';
import LegalPage from '@/pages/LegalPage';
import { legalDocuments } from '@/data/legal';
import { legalNavigation } from '@/data/legal/company';
import { StudioLayout } from '@/components/studio/StudioLayout';
import StudioPage from '@/pages/StudioPage';
import StudioCartPage from '@/pages/StudioCartPage';
import StudioCheckoutPage from '@/pages/StudioCheckoutPage';
import StudioOrderPage from '@/pages/StudioOrderPage';
import AdminProductsPage from '@/pages/AdminProductsPage';

function HomePage() {
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

function RouteScroll() {
  const { pathname } = useLocation();
  useEffect(() => {
    const target = window.location.hash.slice(1);
    const id = requestAnimationFrame(() => {
      if (target && document.getElementById(target)) document.getElementById(target).scrollIntoView();
      else window.scrollTo({ top: 0, behavior: 'instant' });
    });
    return () => cancelAnimationFrame(id);
  }, [pathname]);
  return null;
}

export default function App() {
  return <BrowserRouter><RouteScroll /><Routes><Route path="/" element={<HomePage />} />{['/verwaltung','/verwaltung/dekorationen','/verwaltung/artikel/:productId','/verwaltung/artikel/:productId/vorlagen/:templateId'].map(path=><Route key={path} path={path} element={<AdminProductsPage/>}/>)}{legalNavigation.map(item => <Route key={item.key} path={item.path} element={<LegalPage document={legalDocuments[item.key]} />} />)}<Route element={<StudioLayout />}><Route path="/gestalten" element={<StudioPage />} /><Route path="/warenkorb" element={<StudioCartPage />} /><Route path="/testabschluss" element={<StudioCheckoutPage />} /><Route path="/testbestellung/:id" element={<StudioOrderPage />} /></Route><Route path="*" element={<HomePage />} /></Routes></BrowserRouter>;
}