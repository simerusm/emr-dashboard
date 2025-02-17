'use client'

import { useEffect, useState } from 'react'
import DiffViewer from '../../components/DiffViewer'
import { getProcessedEMR } from '../../lib/emrProcessor'
import type { EMRSection } from '../../lib/types'

interface Props {
  id: string
}

export default function Content({ id }: Props) {
  const [emrData, setEmrData] = useState<EMRSection[]>([])

  useEffect(() => {
    const loadData = async () => {
      const data = await getProcessedEMR(id)
      setEmrData(data)
    }
    loadData()
  }, [id])

  return <DiffViewer emrData={emrData} />
}