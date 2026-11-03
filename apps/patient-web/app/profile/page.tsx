import { ProfileForm } from "../../components/profile-form";
import { PageHeader } from "../../components/ui-primitives";

export default function ProfilePage() {
  return (
    <div className="page-stack page-stack--narrow">
      <PageHeader
        eyebrow="Your patient profile"
        title="Personal details"
        description="Keep the information that supports your health record accurate and up to date."
      />
      <ProfileForm />
    </div>
  );
}
