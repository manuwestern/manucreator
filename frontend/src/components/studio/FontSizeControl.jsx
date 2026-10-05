import { useEffect,useState } from 'react';
import { ChevronDown,Check } from 'lucide-react';
import { Popover,PopoverContent,PopoverTrigger } from '@/components/ui/popover';

const sizes=[8,10,12,14,16,18,20,24,28,32,36,40,48,60,72,96,120,160,200];
const display=value=>String(Math.round(value*10)/10);

export const FontSizeControl=({value,onChange})=>{
  const [text,setText]=useState(display(value)),[open,setOpen]=useState(false),[error,setError]=useState('');
  useEffect(()=>{setText(display(value));setError('');},[value]);
  const valid=raw=>/^\d+(?:[.,]\d+)?$/.test(raw)&&Number(raw.replace(',','.'))>=4&&Number(raw.replace(',','.'))<=200;
  const type=raw=>{setText(raw);setError('');if(valid(raw))onChange(Number(raw.replace(',','.')));};
  const commit=()=>{if(!valid(text)){setError('Bitte eine Größe von 4 bis 200 px eingeben.');return;}onChange(Number(text.replace(',','.')));};
  const choose=size=>{setText(display(size));setError('');setOpen(false);onChange(size);};
  const blur=()=>{if(!valid(text))setError('Bitte eine Größe von 4 bis 200 px eingeben.');};
  const keydown=e=>{
    if(e.key==='Enter'){e.preventDefault();commit();}
    if(e.key==='ArrowDown'){e.preventDefault();setOpen(true);}
    if(e.key==='Escape'){setOpen(false);setText(display(value));setError('');}
  };
  return <div className="font-control-field font-size-field">
    <label htmlFor="text-font-size">Größe</label>
    <Popover open={open} onOpenChange={setOpen}>
      <div className="font-size-combobox">
        <input id="text-font-size" type="text" inputMode="decimal" autoComplete="off"
          aria-label="Schriftgröße in Pixeln" role="combobox" aria-autocomplete="none"
          aria-expanded={open} aria-controls={open?'font-size-options':undefined}
          aria-invalid={!!error} aria-describedby={error?'font-size-entry-error':undefined}
          value={text} onChange={e=>type(e.target.value)} onBlur={blur} onKeyDown={keydown}
          data-testid="text-font-size"/>
        <PopoverTrigger asChild>
          <button type="button" title="Schriftgröße auswählen" aria-label="Schriftgröße auswählen" data-testid="font-size-dropdown"><ChevronDown size={14}/></button>
        </PopoverTrigger>
      </div>
      <PopoverContent align="end" sideOffset={5} className="font-size-menu" data-testid="font-size-menu">
        <div id="font-size-options" role="listbox" aria-label="Schriftgrößen">
          {sizes.map(size=><button type="button" key={size} role="option" aria-selected={value===size} onClick={()=>choose(size)} data-testid={`font-size-option-${size}`}><span>{size} px</span>{value===size&&<Check size={13}/>}</button>)}
        </div>
      </PopoverContent>
    </Popover>
    {error&&<p id="font-size-entry-error" role="alert" className="property-error" data-testid="font-size-entry-error">{error}</p>}
  </div>;
};