import { describe, expect, it, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { useForm } from 'react-hook-form';
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from '../form';

describe('react-hook-form integration', () => {
  it('validates, updates and submits a controlled field through the UI wrapper', async () => {
    const onSubmit = vi.fn();

    function TestForm() {
      const form = useForm({ defaultValues: { name: '' } });
      return (
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)}>
            <FormField
              control={form.control}
              name="name"
              rules={{ required: 'Name is required' }}
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Name</FormLabel>
                  <FormControl><input {...field} /></FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <button type="submit">Save</button>
          </form>
        </Form>
      );
    }

    const user = userEvent.setup();
    render(<TestForm />);
    await user.click(screen.getByRole('button', { name: 'Save' }));

    expect(await screen.findByText('Name is required')).toBeInTheDocument();
    expect(screen.getByLabelText('Name')).toHaveAttribute('aria-invalid', 'true');
    expect(onSubmit).not.toHaveBeenCalled();

    await user.type(screen.getByLabelText('Name'), 'Workflow');
    await user.click(screen.getByRole('button', { name: 'Save' }));

    await waitFor(() => expect(onSubmit).toHaveBeenCalledOnce());
    expect(onSubmit.mock.calls[0][0]).toEqual({ name: 'Workflow' });
    expect(screen.queryByText('Name is required')).not.toBeInTheDocument();
    expect(screen.getByLabelText('Name')).toHaveAttribute('aria-invalid', 'false');
  });
});
