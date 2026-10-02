import { legalDate } from '@/data/legal/company';

export const downloadLegalText = (filename, content) => {
  const url = URL.createObjectURL(new Blob(['\uFEFF', content], { type: 'text/plain;charset=utf-8' }));
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
};

export const documentAsText = document => [
  'MANUCREATOR · MANUEL BAYER',
  document.title.toUpperCase(),
  `Stand: ${legalDate} · ENTWURF ZUR PRÜFUNG`,
  document.note,
  ...document.sections.flatMap(section => [
    section.title,
    ...section.paragraphs,
    ...(section.form ? [section.form] : []),
    ...(section.links || []).map(link => `${link.label}: ${link.href}`),
  ]),
].join('\n\n');