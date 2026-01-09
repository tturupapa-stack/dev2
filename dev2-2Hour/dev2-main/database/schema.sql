-- =====================================================
-- iHerb 건기식 리뷰 팩트체크 시스템 데이터베이스 스키마
-- =====================================================
-- 작성일: 2026-01-05
-- 설명: products와 reviews 테이블 정의
-- =====================================================

-- 1) 제품 테이블
CREATE TABLE IF NOT EXISTS public.products (
  id BIGSERIAL PRIMARY KEY,
  source TEXT NOT NULL DEFAULT 'iherb',
  source_product_id TEXT NOT NULL,             -- iHerb 상품 ID(또는 slug)
  url TEXT,
  title TEXT,
  brand TEXT,
  category TEXT,
  price NUMERIC,
  currency TEXT DEFAULT 'USD',
  rating_avg NUMERIC,
  rating_count INT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE (source, source_product_id)
);

-- 2) 리뷰 테이블
CREATE TABLE IF NOT EXISTS public.reviews (
  id BIGSERIAL PRIMARY KEY,
  product_id BIGINT NOT NULL REFERENCES public.products(id) ON DELETE CASCADE,
  source TEXT NOT NULL DEFAULT 'iherb',
  source_review_id TEXT,                       -- 가능하면(없으면 null)
  author TEXT,
  rating INT,
  title TEXT,
  body TEXT,
  language TEXT DEFAULT 'ko',
  review_date DATE,
  helpful_count INT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  UNIQUE (source, source_review_id)
);

-- 인덱스 생성 (성능 최적화)
CREATE INDEX IF NOT EXISTS idx_products_source ON public.products(source);
CREATE INDEX IF NOT EXISTS idx_products_brand ON public.products(brand);
CREATE INDEX IF NOT EXISTS idx_reviews_product_id ON public.reviews(product_id);
CREATE INDEX IF NOT EXISTS idx_reviews_rating ON public.reviews(rating);
CREATE INDEX IF NOT EXISTS idx_reviews_review_date ON public.reviews(review_date);

-- 업데이트 시간 자동 갱신 함수
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 트리거 생성 (products 업데이트 시 자동 updated_at 갱신)
DROP TRIGGER IF EXISTS update_products_updated_at ON public.products;
CREATE TRIGGER update_products_updated_at
    BEFORE UPDATE ON public.products
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- 코멘트 추가 (테이블 설명)
COMMENT ON TABLE public.products IS 'iHerb 건강기능식품 제품 정보';
COMMENT ON TABLE public.reviews IS 'iHerb 제품 리뷰 데이터';

COMMENT ON COLUMN public.products.source_product_id IS 'iHerb 상품 고유 ID 또는 slug';
COMMENT ON COLUMN public.reviews.product_id IS 'products 테이블 외래키';
COMMENT ON COLUMN public.reviews.source_review_id IS 'iHerb 리뷰 고유 ID (선택)';
COMMENT ON COLUMN public.reviews.helpful_count IS '도움이 됨 투표 수';
