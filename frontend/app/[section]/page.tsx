import Portal from "@/components/Portal";
export default async function SectionPage({ params }: { params: Promise<{ section: string }> }) { const { section } = await params; return <Portal section={section} />; }
