import { Link } from 'react-router-dom';

export const LegalLink = ({ href, children, testId, ...props }) => href.startsWith('/')
  ? <Link to={href} data-testid={testId} {...props}>{children}</Link>
  : <a href={href} data-testid={testId} {...(href.startsWith('https://') ? { target: '_blank', rel: 'noopener noreferrer' } : {})} {...props}>{children}</a>;

export const LegalSection = ({ section, documentKey }) => {
  const prefix = `legal-${documentKey}-${section.id}`;
  return <section className="legal-section" id={section.id} data-testid={prefix}>
    <h2 data-testid={`${prefix}-title`}>{section.title}</h2>
    {section.paragraphs.map((text, i) => <p key={i} data-testid={`${prefix}-paragraph-${i}`}>{text}</p>)}
    {section.form && <pre className="withdrawal-template" data-testid="withdrawal-template">{section.form}</pre>}
    {section.links && <div className="legal-section-links">{section.links.map((link, i) => <LegalLink key={link.href} href={link.href} testId={`${prefix}-link-${i}`}>{link.label}</LegalLink>)}</div>}
  </section>;
};