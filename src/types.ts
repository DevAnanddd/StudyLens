/**
 * StudyLens Core Types & Interfaces
 */

export interface SlideOCRInput {
  id: string;
  filename: string;
  pageNumber: number;
  rawOcr: string;
  detectedHeader?: string;
  metadata?: Record<string, any>;
}

export interface TaggedSlide {
  slideId: string;
  topic: string;
  subtopic?: string;
  keywords: string[];
  slideType: "content" | "title_slide" | "outline" | "review" | "qa";
  confidence: number;
}

export interface TopicCluster {
  id: string;
  topicName: string;
  normalizedKey: string;
  slideIds: string[];
  slides: SlideOCRInput[];
  sources: Array<{ filename: string; pageNumber: number }>;
  status: "pending" | "processing" | "completed" | "error";
  generatedMarkdown?: string;
  error?: string;
}

export interface StudyNoteSection {
  topic: string;
  overview: string[];
  importantConcepts: string[];
  definitions: Array<{ term: string; definition: string }>;
  keyPoints: string[];
  examRevision: string[];
  sources: string[];
  rawMarkdown: string;
}

export interface MasterRevisionDoc {
  title: string;
  generatedAt: string;
  totalSlides: number;
  tableOfContents: Array<{ title: string; anchor: string; slideCount: number }>;
  sections: StudyNoteSection[];
  deduplicatedDefinitions: Array<{
    term: string;
    definition: string;
    topics: string[];
    sources: string[];
  }>;
  fullMarkdown: string;
}

export type PipelineStage =
  | "idle"
  | "tagging"
  | "clustering"
  | "summarizing"
  | "assembling"
  | "completed"
  | "error";

export interface PipelineProgress {
  stage: PipelineStage;
  message: string;
  currentBatch: number;
  totalBatches: number;
  taggedSlides: number;
  totalSlides: number;
  completedClusters: number;
  totalClusters: number;
  percentage: number;
}

export interface PipelineConfig {
  taggingBatchSize: number;
  summarizeBatchSize: number;
  modelName: string;
  taggingTemperature: number;
  summarizeTemperature: number;
  maxConcurrency: number;
  enableSimulationFallback: boolean;
}
