import { NextResponse } from 'next/server';

export async function GET() {
  return NextResponse.json({
    status: 'ok',
    message: '365 Curated B2B Sales Quotes Database Active',
    authoritiesCount: 40,
    totalQuotes: 365
  });
}
