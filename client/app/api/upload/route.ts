import { NextResponse } from "next/server"

// TODO: NOT USED YET, REFACT TO ENFORCE PROXY FOR VALIDATION

export async function POST(request: Request) {
  try {
    const response = await fetch(
      `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5003'}/analyze`,
      {
        method: 'POST',
        body: request.body,
        headers: request.headers,
      }
    );
  
    const analysisData = await response.json();

    if (!('fileId' in analysisData) || !('data' in analysisData)) {
      return NextResponse.json({ error: 'Invalid response format from analysis service' }, { status: 500 })
    }

    return NextResponse.json({ 
      message: "File uploaded successfully",
      fileId: analysisData.fileId,
      data: analysisData.data
    }, { status: 200 })
    
  } catch (error) {
    console.error('Error processing upload:', error)
    return NextResponse.json({ 
      error: "Error processing upload" 
    }, { status: 500 })
  }
}