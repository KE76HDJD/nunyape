import React from 'react';
import { DragDropContext, Droppable, Draggable } from 'react-beautiful-dnd';
import { GripVertical, Eye, Trash2, Copy } from 'lucide-react';

const SlideManager = ({ 
  slides, 
  currentSlide, 
  onSlideSelect, 
  onSlideUpdate, 
  onSlideAdd,
  onSlideDelete,
  onSlideDuplicate 
}) => {
  const handleDragEnd = (result) => {
    if (!result.destination) return;
    
    const items = Array.from(slides);
    const [reorderedItem] = items.splice(result.source.index, 1);
    items.splice(result.destination.index, 0, reorderedItem);
    
    // Mettre à jour l'ordre des slides
    onSlideUpdate(items);
  };

  const duplicateSlide = (slideIndex) => {
    const slideToDuplicate = slides[slideIndex];
    const duplicatedSlide = {
      ...slideToDuplicate,
      id: Date.now(),
      title: `${slideToDuplicate.title} (Copie)`
    };
    
    const newSlides = [...slides];
    newSlides.splice(slideIndex + 1, 0, duplicatedSlide);
    onSlideUpdate(newSlides);
    onSlideSelect(slideIndex + 1);
  };

  const deleteSlide = (slideIndex) => {
    if (slides.length <= 1) return;
    
    const newSlides = slides.filter((_, index) => index !== slideIndex);
    onSlideUpdate(newSlides);
    
    if (currentSlide >= slideIndex && currentSlide > 0) {
      onSlideSelect(currentSlide - 1);
    }
  };

  return (
    <div className="p-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">Slides</h3>
        <span className="text-sm text-gray-500">{slides.length} slides</span>
      </div>

      <DragDropContext onDragEnd={handleDragEnd}>
        <Droppable droppableId="slides">
          {(provided) => (
            <div
              {...provided.droppableProps}
              ref={provided.innerRef}
              className="space-y-2"
            >
              {slides.map((slide, index) => (
                <Draggable
                  key={slide.id}
                  draggableId={String(slide.id)}
                  index={index}
                >
                  {(provided, snapshot) => (
                    <div
                      ref={provided.innerRef}
                      {...provided.draggableProps}
                      className={`p-3 border rounded-lg cursor-pointer transition-all ${
                        currentSlide === index
                          ? 'border-primary-500 bg-primary-50'
                          : 'border-gray-200 hover:border-gray-300'
                      } ${
                        snapshot.isDragging ? 'shadow-lg bg-white' : 'bg-white'
                      }`}
                      onClick={() => onSlideSelect(index)}
                    >
                      <div className="flex items-center justify-between">
                        <div {...provided.dragHandleProps}>
                          <GripVertical className="h-4 w-4 text-gray-400" />
                        </div>
                        
                        <div className="flex-1 ml-2">
                          <h4 className="text-sm font-medium text-gray-900 truncate">
                            {slide.title || `Slide ${index + 1}`}
                          </h4>
                          <p className="text-xs text-gray-500 truncate">
                            {slide.content?.substring(0, 50)}...
                          </p>
                        </div>
                        
                        <div className="flex items-center space-x-1 opacity-0 group-hover:opacity-100 transition-opacity">
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              duplicateSlide(index);
                            }}
                            className="p-1 hover:bg-gray-100 rounded transition-colors"
                          >
                            <Copy className="h-3 w-3 text-gray-500" />
                          </button>
                          
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              deleteSlide(index);
                            }}
                            disabled={slides.length <= 1}
                            className="p-1 hover:bg-gray-100 rounded transition-colors disabled:opacity-50"
                          >
                            <Trash2 className="h-3 w-3 text-gray-500" />
                          </button>
                        </div>
                      </div>
                    </div>
                  )}
                </Draggable>
              ))}
              {provided.placeholder}
            </div>
          )}
        </Droppable>
      </DragDropContext>

      <button
        onClick={onSlideAdd}
        className="w-full mt-4 py-2 border-2 border-dashed border-gray-300 rounded-lg text-gray-500 hover:text-gray-700 hover:border-gray-400 transition-colors"
      >
        + Ajouter une slide
      </button>
    </div>
  );
};

export default SlideManager;