import { address } from './company';

const contact = `${address}, E-Mail: info@manucreator.de`;
const declaration = `Um Ihr Widerrufsrecht auszuüben, müssen Sie uns (${contact}) mittels einer eindeutigen Erklärung (z. B. ein mit der Post versandter Brief oder eine E-Mail) über Ihren Entschluss, diesen Vertrag zu widerrufen, informieren. Sie können dafür das unten stehende Muster-Widerrufsformular verwenden, das jedoch nicht vorgeschrieben ist.`;
const deadline = 'Zur Wahrung der Widerrufsfrist reicht es aus, dass Sie die Mitteilung über die Ausübung des Widerrufsrechts vor Ablauf der Widerrufsfrist absenden.';
const refund = 'Wenn Sie diesen Vertrag widerrufen, haben wir Ihnen alle Zahlungen, die wir von Ihnen erhalten haben, einschließlich der Lieferkosten (mit Ausnahme der zusätzlichen Kosten, die sich daraus ergeben, dass Sie eine andere Art der Lieferung als die von uns angebotene, günstigste Standardlieferung gewählt haben), unverzüglich und spätestens binnen vierzehn Tagen ab dem Tag zurückzuzahlen, an dem die Mitteilung über Ihren Widerruf dieses Vertrags bei uns eingegangen ist. Für diese Rückzahlung verwenden wir dasselbe Zahlungsmittel, das Sie bei der ursprünglichen Transaktion eingesetzt haben, es sei denn, mit Ihnen wurde ausdrücklich etwas anderes vereinbart; in keinem Fall werden Ihnen wegen dieser Rückzahlung Entgelte berechnet.';

export const withdrawalForm = `MUSTER-WIDERRUFSFORMULAR\n\n(Wenn Sie den Vertrag widerrufen wollen, dann füllen Sie bitte dieses Formular aus und senden Sie es zurück.)\n\nAn: Manuel Bayer · ManuCreator\nBüttgerwald 16\n47877 Willich\nDeutschland\nE-Mail: info@manucreator.de\n\nHiermit widerrufe(n) ich/wir (*) den von mir/uns (*) abgeschlossenen Vertrag über den Kauf der folgenden Waren (*) / die Erbringung der folgenden Dienstleistung (*):\n\n____________________________________________________________\n\nBestellt am (*) / erhalten am (*): ___________________________\n\nName des/der Verbraucher(s): _________________________________\n\nAnschrift des/der Verbraucher(s): ____________________________\n\n____________________________________________________________\n\nUnterschrift des/der Verbraucher(s) (nur bei Mitteilung auf Papier):\n\n____________________________________________________________\n\nDatum: ______________________________________________________\n\n(*) Unzutreffendes streichen.\n\nDie Verwendung dieses Formulars ist freiwillig. Ein Widerruf muss nicht begründet werden. Eine E-Mail ist ohne handschriftliche Unterschrift möglich.\n`;

export const withdrawal = {
  key: 'withdrawal',
  title: 'Widerrufsbelehrung',
  subtitle: 'Informationen für Verbraucher und Muster-Widerrufsformular',
  note: 'Entwurf: Die geschäftliche Telefonnummer fehlt noch. Vor verbindlichen Verbraucheraufträgen müssen die Angaben ergänzt, die zum konkreten Auftrag passende Belehrung ausgewählt und rechtlich geprüft werden. Ein gesetzliches Widerrufsrecht wird durch diesen Hinweis nicht eingeschränkt.',
  sections: [
    { id: 'einordnung', title: 'Welche Regelung gilt für deinen Auftrag?', paragraphs: [
      'Diese Informationen betreffen Verbraucher bei Fernabsatzverträgen oder außerhalb von Geschäftsräumen geschlossenen Verträgen. Unternehmern steht das gesetzliche Verbraucher-Widerrufsrecht nicht zu. Eine unverbindliche Anfrage über diese Website ist noch kein Vertrag und muss nicht widerrufen werden.',
      'Für nicht personalisierte Waren gilt grundsätzlich Abschnitt A. Für Dienstleistungen beziehungsweise entsprechend einzuordnende Arbeiten an kundeneigenen Gegenständen gilt grundsätzlich Abschnitt B. Die Ausnahme für bestimmte personalisierte Waren ist in Abschnitt C erläutert. Maßgeblich bleibt die rechtliche Einordnung des konkreten Vertrags.',
    ] },
    { id: 'waren', title: 'A. Widerrufsrecht für nicht personalisierte Waren', paragraphs: [
      'Sie haben das Recht, binnen vierzehn Tagen ohne Angabe von Gründen diesen Vertrag zu widerrufen.',
      'Die Widerrufsfrist beträgt vierzehn Tage ab dem Tag, an dem Sie oder ein von Ihnen benannter Dritter, der nicht der Beförderer ist, die Waren in Besitz genommen haben bzw. hat. Bei mehreren Waren aus einer einheitlichen Bestellung, die getrennt geliefert werden, beginnt die Frist mit dem Erhalt der letzten Ware; bei einer Ware in mehreren Teilsendungen oder Stücken mit dem Erhalt der letzten Teilsendung beziehungsweise des letzten Stücks.',
      declaration,
      deadline,
    ] },
    { id: 'warenfolgen', title: 'Folgen des Widerrufs bei Waren', paragraphs: [
      refund,
      'Wir können die Rückzahlung verweigern, bis wir die Waren wieder zurückerhalten haben oder bis Sie den Nachweis erbracht haben, dass Sie die Waren zurückgesandt haben, je nachdem, welches der frühere Zeitpunkt ist.',
      `Sie haben die Waren unverzüglich und in jedem Fall spätestens binnen vierzehn Tagen ab dem Tag, an dem Sie uns über den Widerruf dieses Vertrags unterrichten, an ${address} zurückzusenden oder zu übergeben. Die Frist ist gewahrt, wenn Sie die Waren vor Ablauf der Frist von vierzehn Tagen absenden.`,
      'Sie tragen die unmittelbaren Kosten der Rücksendung der Waren. Für Waren, die nicht auf dem normalen Postweg zurückgesandt werden können, sind die konkreten oder geschätzten Rücksendekosten vor dem jeweiligen Vertragsschluss gesondert mitzuteilen. Fehlt eine gesetzlich erforderliche Kosteninformation, gelten die gesetzlichen Folgen; eine fehlende Angabe wird durch diesen allgemeinen Hinweis nicht ersetzt.',
      'Sie müssen für einen etwaigen Wertverlust der Waren nur aufkommen, wenn dieser Wertverlust auf einen zur Prüfung der Beschaffenheit, Eigenschaften und Funktionsweise der Waren nicht notwendigen Umgang mit ihnen zurückzuführen ist.',
    ] },
    { id: 'leistungen', title: 'B. Widerrufsrecht bei Dienstleistungen und Bearbeitungsaufträgen', paragraphs: [
      'Sie haben das Recht, binnen vierzehn Tagen ohne Angabe von Gründen diesen Vertrag zu widerrufen.',
      'Die Widerrufsfrist beträgt vierzehn Tage ab dem Tag des Vertragsabschlusses.',
      declaration,
      deadline,
    ] },
    { id: 'leistungsfolgen', title: 'Folgen des Widerrufs bei Dienstleistungen', paragraphs: [
      refund,
      'Haben Sie verlangt, dass die Dienstleistungen während der Widerrufsfrist beginnen sollen, so haben Sie uns einen angemessenen Betrag zu zahlen, der dem Anteil der bis zu dem Zeitpunkt, zu dem Sie uns von der Ausübung des Widerrufsrechts hinsichtlich dieses Vertrags unterrichten, bereits erbrachten Dienstleistungen im Vergleich zum Gesamtumfang der im Vertrag vorgesehenen Dienstleistungen entspricht. Dies setzt die gesetzlichen Voraussetzungen für einen Wertersatzanspruch, insbesondere eine ordnungsgemäße Belehrung und ein ausdrückliches Verlangen, voraus.',
      'Bei entgeltlichen Dienstleistungen erlischt das Widerrufsrecht erst mit vollständiger Erbringung der Dienstleistung, wenn Sie vor Beginn ausdrücklich zugestimmt haben, dass die Leistung vor Ablauf der Widerrufsfrist beginnt, und Ihre Kenntnis bestätigt haben, dass Ihr Widerrufsrecht mit vollständiger Vertragserfüllung durch ManuCreator erlischt. Bei außerhalb von Geschäftsräumen geschlossenen Verträgen muss die Zustimmung auf einem dauerhaften Datenträger übermittelt werden. Die Voraussetzungen richten sich nach § 356 BGB.',
      'Eine solche Erklärung wird gegebenenfalls gesondert zum Auftrag eingeholt. Das Lesen der AGB, die bloße Kontaktanfrage und eine Zahlung ersetzen sie nicht. Ohne wirksame Erklärung wird ein entsprechender Auftrag grundsätzlich erst nach Ablauf der Widerrufsfrist begonnen.',
    ] },
    { id: 'personalisierung', title: 'C. Ausnahme für bestimmte personalisierte Waren', paragraphs: [
      'Nach § 312g Absatz 2 Nummer 1 BGB besteht, soweit nichts anderes vereinbart wurde, kein Widerrufsrecht bei Verträgen zur Lieferung von Waren, die nicht vorgefertigt sind und für deren Herstellung eine individuelle Auswahl oder Bestimmung durch den Verbraucher maßgeblich ist oder die eindeutig auf die persönlichen Bedürfnisse des Verbrauchers zugeschnitten sind.',
      'Dies kann beispielsweise eine individuell mit einem persönlichen Namen oder einem kundenspezifischen Motiv gefertigte Ware betreffen. Nicht jede Auswahl aus Standardvarianten erfüllt automatisch diese Ausnahme. Ob die Ausnahme greift, muss für den konkreten Auftrag geprüft und vor Vertragsschluss mitgeteilt werden.',
      'Die Ausnahme gilt nicht pauschal für die Bearbeitung eines Gegenstands, der dem Kunden bereits gehört. Auch bei einer vom Widerruf ausgenommenen personalisierten Ware bleiben gesetzliche Mängelrechte erhalten.',
    ] },
    { id: 'musterformular', title: 'D. Muster-Widerrufsformular', paragraphs: ['Das Formular ist freiwillig. Du kannst deinen Widerruf auch mit einer anderen eindeutigen Erklärung per E-Mail oder Brief übermitteln. Es ist weder eine Begründung noch bei einer E-Mail eine handschriftliche Unterschrift erforderlich.'], form: withdrawalForm },
  ],
};