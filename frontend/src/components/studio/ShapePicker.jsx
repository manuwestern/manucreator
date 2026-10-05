import { useState } from 'react';
import { Minus,Circle,Square,Heart,Triangle,Star,Shapes } from 'lucide-react';
import { Popover,PopoverContent,PopoverTrigger } from '@/components/ui/popover';
import { shapeNames } from '@/lib/studioShapes';
import '@/styles/studio-shapes.css';

const options=[[Minus,'line'],[Circle,'circle'],[Square,'rectangle'],[Heart,'heart'],[Triangle,'triangle'],[Star,'star']];
export const ShapePicker=({onAdd,disabled})=>{
  const [open,setOpen]=useState(false);
  return <Popover open={open} onOpenChange={setOpen}><PopoverTrigger asChild><button type="button" className="editor-add-button" title="Formen hinzufügen" aria-label="Formen hinzufügen" disabled={disabled} data-testid="shape-picker-open"><Shapes size={17}/><span>Formen</span></button></PopoverTrigger><PopoverContent className="shape-picker" align="start" sideOffset={7} data-testid="shape-picker"><div role="group" aria-label="Grundformen">{options.map(([Icon,type])=><button type="button" disabled={disabled} key={type} onClick={()=>{onAdd(type);setOpen(false);}} data-testid={`add-shape-${type}`}><Icon size={24}/><span>{shapeNames[type]}</span></button>)}</div></PopoverContent></Popover>;
};