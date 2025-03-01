import Content from './Content'

interface Props {
  params: {
    id: string
  }
}

export default async function EMRPage({ params }: Props) {
  const { id } = await Promise.resolve(params)

  return (
    <main className="container mx-auto p-4">
      <Content id={id} />
    </main>
  )
}